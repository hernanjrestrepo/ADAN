"""Nivel 1 Service — the core business logic for Level 1 (El Dolor).

Implements the complete Level 1 flow per AD-FUNC-01:
1. Onboarding (pain discovery)
2. Dynamic questions
3. Board Room (real consensus)
4. Diagnosis
5. Recommendations
6. Gate Review (80/100 threshold)
7. Gemelo Digital persistence
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.router import for_tier
from app.nivel1 import discovery
from app.nivel1.context import ContextLayers
from app.ai.base import LLMAdapter, LLMMessage
from app.ai.normalize import normalize_string, normalize_list
from app.models.models import (
    Card, CardStatus, Company, Conversation, Decision, DecisionStatus,
    Document, Event, Level, Message, NivelStatus, Project, Score, ScoreType,
)
from app.nivel1.board_room import BoardRoom, BoardConsensus
from app.nivel1.gate_review import GateReviewResult, build_result
from app.scoring import service as scoring
from app.services.gemelo_digital import GemeloDigitalService

# Mensajes recientes que se envían completos al modelo; los anteriores van resumidos
MAX_CONTEXT_MESSAGES = 12
MAX_SUMMARY_CHARS = 2000


def discovery_progress(db: Session, conversation: Conversation | None, project: Project) -> dict:
    """Avance del guion para la interfaz; la evidencia ya registrada no se vuelve a sugerir."""
    history = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(
        Message.created_at).all() if conversation else []
    state = discovery.current_state(history)
    known = {e.claim.strip().lower() for e in scoring.active_evidence(db, project, "problem", include_unconfirmed=True)}
    state["evidencia_sugerida"] = [e for e in state["evidencia_sugerida"] if e["afirmacion"].strip().lower() not in known]
    return discovery.progress(state)


class Nivel1Service:
    """Orchestrates the complete Level 1 flow with real intelligence."""

    def __init__(self, llm: LLMAdapter, db: Session):
        # Conversación, diagnóstico y recomendaciones: nivel "standard" (WO-099)
        self.llm = for_tier(llm, "standard")
        self.db = db
        self.gemelo = GemeloDigitalService(db)
        self.board_room = BoardRoom(llm)

    # --- Step 1: Pain Discovery Card ---

    def get_or_create_pain_card(self, project: Project, level: Level) -> Card:
        """Get or create the Pain Discovery card for Level 1."""
        card = self.db.query(Card).filter(
            Card.project_id == project.id,
            Card.level_id == level.id,
            Card.card_type == "pain_discovery",
        ).first()

        if not card:
            card = Card(
                project_id=project.id,
                level_id=level.id,
                title="Descubrimiento del Dolor",
                description="¿Qué problema real resuelve tu empresa? ¿A quién afecta? ¿Qué tan urgente es?",
                card_type="pain_discovery",
                status=CardStatus.ACTIVE,
            )
            self.db.add(card)
            self.db.commit()
            self.db.refresh(card)

        return card

    def get_or_create_conversation(self, card: Card) -> Conversation:
        """Get or create conversation for a card."""
        conv = self.db.query(Conversation).filter(
            Conversation.card_id == card.id,
            Conversation.status == "active",
        ).first()

        if not conv:
            conv = Conversation(
                card_id=card.id,
                title="Conversación de Descubrimiento",
            )
            self.db.add(conv)
            self.db.commit()
            self.db.refresh(conv)

        return conv

    # --- Step 2: Chat with ADÁN ---

    async def chat(
        self,
        project: Project,
        level: Level,
        user_message: str,
        conversation: Conversation | None = None,
    ) -> tuple[Message, Conversation]:
        """Un turno del guion de descubrimiento: ADÁN entiende la respuesta y hace la siguiente pregunta.

        Una sola llamada con salida estructurada devuelve la respuesta y el estado de los siete temas
        (discovery.py). Si responde el modelo local de respaldo, el estado no se toca y el mensaje
        queda marcado como degradado para que el cliente lo sepa.
        """
        card = self.get_or_create_pain_card(project, level)
        if conversation is None:
            conversation = self.get_or_create_conversation(card)

        self.db.add(Message(conversation_id=conversation.id, role="user", content=user_message))
        self.db.commit()

        state = discovery.current_state(self._history(conversation))
        messages = self.build_llm_messages(conversation, state)
        response = await self.llm.chat_json(messages, discovery.SCHEMA, temperature=0.4, max_tokens=2048)

        degraded = response.metadata.get("degraded")
        parsed = response.parsed if isinstance(response.parsed, dict) else {}
        reply = parsed.get("respuesta") if isinstance(parsed.get("respuesta"), str) else ""
        if reply.strip():
            content = reply.strip()
            if not degraded:
                state = discovery.merge(state, parsed)
        elif response.content.strip() and not response.content.lstrip().startswith(("{", "[")):
            content = response.content.strip()  # el modelo respondió en texto: se muestra tal cual
        else:
            content = ("No pude procesar tu mensaje esta vez. Quedó guardado: escríbeme de nuevo la idea "
                       "principal y seguimos donde íbamos.")

        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            agent_name="ADÁN",
            content=content,
            metadata_json={
                "model": response.model,
                "tokens": response.prompt_tokens + response.completion_tokens,
                "duration_s": response.duration_s,
                "degraded": degraded,
                "discovery": state,
            },
        )
        self.db.add(assistant_msg)
        self.db.commit()
        self.db.refresh(assistant_msg)

        return assistant_msg, conversation

    def _history(self, conversation: Conversation) -> list[Message]:
        return self.db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()

    def build_llm_messages(self, conversation: Conversation, state: dict | None = None,
                           structured: bool = True) -> list[LLMMessage]:
        """Contexto para el modelo: guion y estado, resumen de lo antiguo y los mensajes recientes completos.

        Evita desbordar la ventana de contexto en conversaciones largas (AD-CMP-04).
        """
        history = self._history(conversation)
        if state is None:
            state = discovery.current_state(history)
        older, recent = history[:-MAX_CONTEXT_MESSAGES], history[-MAX_CONTEXT_MESSAGES:]
        if older:
            conversation.summary = self._summarize(older)
            self.db.commit()

        system_prompt = discovery.system_prompt(state, structured=structured)
        if conversation.summary:
            system_prompt += f"\n\nResumen de lo que el cliente contó antes: {conversation.summary}"
        # Capas Global, Proyecto, Nivel y Card (AD-CMP-04); la Conversación son los mensajes
        system_prompt += "\n\n" + ContextLayers(self.db).for_conversation(conversation)
        messages = [LLMMessage(role="system", content=system_prompt)]
        for msg in recent:
            messages.append(LLMMessage(role=msg.role, content=msg.content))
        return messages

    @staticmethod
    def _summarize(messages: list[Message]) -> str:
        """Resumen extractivo de lo que el usuario ya contó (sin llamar al modelo)."""
        summary = " | ".join(m.content[:200] for m in messages if m.role == "user")
        return summary[:MAX_SUMMARY_CHARS]

    # --- Step 3: Board Room ---

    async def run_board_room(self, project: Project, company: Company,
                             client_question: str = "", client_position: str = "") -> BoardConsensus:
        """Board Room de 7 roles (AD-FUNC-02): el CEO preside y seis especialistas votan."""
        pain_description = self.board_brief(project)
        if not pain_description.strip():
            raise ValueError("No hay descripción del dolor. Inicia una conversación primero.")
        conversation_context = ""

        # El Board también ve lo que ya se sabe de la empresa (capa Proyecto, AD-CMP-04)
        conversation_context += "\n\nLo que ya se sabe de la empresa:\n" + ContextLayers(self.db).project_layer(project)

        consensus = await self.board_room.run(pain_description, conversation_context,
                                              client_question=client_question, client_position=client_position)

        # Persist result in Gemelo Digital
        votes_data = [
            {
                "agent": v.agent,
                "vote": v.vote,
                "confidence": v.confidence,
                "justification": v.justification,
            }
            for v in consensus.votes
        ]

        self.gemelo.save_board_room_result(
            project,
            consensus.decision,
            consensus.score,
            consensus.summary,
            votes_data,
            consensus=consensus.to_dict(),
        )
        self.gemelo.save_board_minutes(project, consensus.minutes)
        # El voto del Board entra como inferencia sobre el problema: la evidencia más débil (AD-CMP-05)
        if scoring.record_board_inference(self.db, project, consensus) is not None:
            self.db.commit()

        return consensus

    def board_brief(self, project: Project) -> str:
        """Lo que el Board evalúa: lo que ADÁN entendió (guion), la evidencia registrada y las palabras
        del cliente. Las respuestas del modelo de respaldo y el resto de la charla no entran: antes el
        Board leía la conversación cruda, con ruido y respuestas sin sentido."""
        card = self.db.query(Card).filter(Card.project_id == project.id, Card.card_type == "pain_discovery").first()
        conversation = self.db.query(Conversation).filter(Conversation.card_id == card.id).first() if card else None
        history = self._history(conversation) if conversation else []
        state = discovery.current_state(history)
        parts = []
        understood = discovery.brief(state)
        if understood:
            parts.append("Lo que ADÁN entendió del dolor (guion del Nivel 1):\n" + understood)
        evidence = scoring.active_evidence(self.db, project, "problem")
        if evidence:
            labels = {"external": "fuente externa", "testimony": "testimonio de clientes", "inference": "inferencia"}
            parts.append("Evidencia registrada:\n" + "\n".join(
                f"- [{labels.get(e.kind, e.kind)}{', en contra' if e.polarity == 'contradicts' else ''}] {e.claim}"
                + (f" (fuente: {e.source})" if e.source else "") for e in evidence[:15]))
        else:
            parts.append("Evidencia registrada: ninguna.")
        words = [m.content.strip()[:800] for m in history if m.role == "user" and len(m.content.strip()) >= 10]
        if words:
            parts.append("Palabras del cliente (lo más reciente):\n" + "\n".join(f"- {w}" for w in words[-6:]))
        return "\n\n".join(parts) if (understood or words) else ""

    def get_last_board_consensus(self, project: Project) -> BoardConsensus:
        """Último Board Room guardado: recomendaciones y Gate Review no lo vuelven a ejecutar."""
        data = self.gemelo.get_last_board_consensus(project)
        if data is None:
            raise ValueError("Ejecuta primero el Board Room o el diagnóstico.")
        return BoardConsensus.from_dict(data)

    # --- Step 4: Generate Diagnosis ---

    async def generate_diagnosis(
        self,
        project: Project,
        company: Company,
        board_consensus: BoardConsensus,
    ) -> Document:
        """Generate the formal diagnosis document."""

        # ALL data from board_consensus is already normalized via board_room.py
        # Use normalize_list/normalize_string as safety net
        board_summary = "\n\n".join([
            f"### Análisis {v.agent}\n"
            f"**Voto:** {v.vote} (confianza: {v.confidence:.0f}%)\n"
            f"**Justificación:** {normalize_string(v.justification)}\n"
            f"**Análisis:** {normalize_string(v.analysis)}\n"
            f"**Fortalezas:** {', '.join(normalize_list(v.key_strengths))}\n"
            f"**Preocupaciones:** {', '.join(normalize_list(v.key_concerns))}\n"
            f"**Preguntas pendientes:** {', '.join(normalize_list(v.questions))}"
            for v in board_consensus.votes
        ])

        prompt = (
            f"Genera un Diagnóstico del Dolor formal basado en:\n\n"
            f"## Decisión del Board Room\n"
            f"Decisión: {board_consensus.decision}\n"
            f"Score: {board_consensus.score:.0f}/100\n"
            f"Confianza: {board_consensus.confidence:.0f}%\n\n"
            f"## Análisis de cada Agente\n{board_summary}\n\n"
            f"## Preocupaciones del Board\n"
            f"Unánimes: {', '.join(board_consensus.concerns_unanimous) if board_consensus.concerns_unanimous else 'Ninguna'}\n"
            f"Mayoría: {', '.join(board_consensus.concerns_majority[:5]) if board_consensus.concerns_majority else 'Ninguna'}\n\n"
            f"El diagnóstico debe incluir:\n"
            f"1. Resumen ejecutivo del problema\n"
            f"2. Evidencia que respalda la existencia del problema\n"
            f"3. Análisis del Board Room (síntesis de los 4 agentes)\n"
            f"4. Evaluación de viabilidad\n"
            f"5. Recomendación final con nivel de confianza\n\n"
            f"Formato: Markdown profesional. Sé directo y honesto."
        )

        response = await self.llm.generate(
            prompt=prompt,
            system="Diagnóstico ADÁN. Profesional, honesto. Español.",
            temperature=0.5,
            max_tokens=1024,
        )

        # Save in Gemelo Digital
        doc = self.gemelo.save_diagnosis(project, "Diagnóstico del Dolor", response.content)

        return doc

    # --- Step 5: Generate Recommendations ---

    async def generate_recommendations(
        self,
        project: Project,
        diagnosis: str,
        board_consensus: BoardConsensus,
    ) -> Document:
        """Generate actionable recommendations."""
        prompt = (
            f"Basado en el siguiente diagnóstico y análisis del Board Room, "
            f"genera recomendaciones ACCIONABLES para el emprendedor:\n\n"
            f"## Diagnóstico\n{diagnosis}\n\n"
            f"## Decisión del Board: {board_consensus.decision}\n\n"
            f"## Preocupaciones a abordar\n"
            f"{chr(10).join(f'- {c}' for c in board_consensus.concerns_majority[:5])}\n\n"
            f"Las recomendaciones deben ser:\n"
            f"1. Específicas (no genéricas)\n"
            f"2. Accionables (el emprendedor puede hacerlas ahora)\n"
            f"3. Priorizadas (qué hacer primero)\n"
            f"4. Con evidencia del Board Room que las respalde\n\n"
            f"Formato: Markdown con lista numerada."
        )

        response = await self.llm.generate(
            prompt=prompt,
            system="Eres el asesor de recomendaciones de ADÁN. Genera recomendaciones específicas, accionables y priorizadas. Habla en español.",
            temperature=0.5,
            max_tokens=1536,
        )

        doc = self.gemelo.save_recommendation(project, "Recomendaciones del Nivel 1", response.content)

        return doc

    # --- Step 6: Calculate Scores ---

    async def calculate_scores(
        self,
        project: Project,
        board_consensus: BoardConsensus,
        diagnosis: str,
    ) -> list[Score]:
        """Problem Score sobre la evidencia registrada (AD-CMP-05), no sobre el texto del diagnóstico."""
        return [scoring.calculate_dimension(self.db, project, "problem")]

    # --- Step 7: Gate Review ---

    async def run_gate_review(self, project: Project) -> tuple[GateReviewResult, Decision | None]:
        """Gate del Nivel 1 sobre la evidencia registrada (WO-107).

        Si la evidencia alcanza, propone cerrar el Nivel; se completa solo cuando el cliente lo aprueba.
        """
        evaluation, _score = scoring.evaluate_gate(self.db, project, 1)
        result = build_result(1, evaluation)
        decision = None
        if result.approved:
            decision = self.gemelo.propose_level_completion(project, 1, result.overall_score, result.message)
        return result, decision

    async def run_gate_review_preview(self, project: Project) -> tuple[GateReviewResult, None]:
        """La misma evaluación, sin proponer nada ni guardar un Score nuevo."""
        rule = scoring.engine.GATE_RULES[1]
        rows = scoring.active_evidence(self.db, project, rule.score_type)
        return build_result(1, scoring.engine.evaluate_gate(1, scoring._items(rows))), None

    def advance_without_evidence(self, project: Project) -> Decision:
        """El cliente quiere avanzar sin evidencia suficiente (AD-CMP-01 §3).

        ADÁN no bloquea ni decide por él: propone la decisión recomendando seguir trabajando el
        Nivel. Elegir cerrarlo es decidir distinto a lo recomendado y exige los 6 campos.
        """
        evaluation, _score = scoring.evaluate_gate(self.db, project, 1)
        if evaluation.sufficient:
            raise ValueError("La evidencia ya alcanza: usa el Gate Review para proponer el cierre.")
        result = build_result(1, evaluation)
        return self.gemelo.propose_level_completion(project, 1, result.overall_score, result.message,
                                                    recommended="CONTINUE")
