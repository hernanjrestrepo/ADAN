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
from app.ai.base import LLMAdapter, LLMMessage
from app.ai.normalize import normalize_string, normalize_list
from app.core.disclaimer import strip_disclaimer
from app.models.models import (
    Card, CardStatus, Company, Conversation, Decision, DecisionStatus,
    Document, Event, Level, Message, NivelStatus, Project, Score, ScoreType,
)
from app.nivel1.board_room import BoardRoom, BoardConsensus
from app.nivel1.gate_review import GateReviewEngine, GateReviewResult
from app.services.gemelo_digital import GemeloDigitalService

# Mensajes recientes que se envían completos al modelo; los anteriores van resumidos
MAX_CONTEXT_MESSAGES = 12
MAX_SUMMARY_CHARS = 2000


class Nivel1Service:
    """Orchestrates the complete Level 1 flow with real intelligence."""

    def __init__(self, llm: LLMAdapter, db: Session):
        # Conversación, diagnóstico y recomendaciones: nivel "standard" (WO-099)
        self.llm = for_tier(llm, "standard")
        self.db = db
        self.gemelo = GemeloDigitalService(db)
        self.board_room = BoardRoom(llm)
        self.gate_review = GateReviewEngine()  # Deterministic, no LLM needed

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
        """Process a user message through the AI and return the response."""
        card = self.get_or_create_pain_card(project, level)
        if conversation is None:
            conversation = self.get_or_create_conversation(card)

        # Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=user_message,
        )
        self.db.add(user_msg)
        self.db.commit()

        messages = self.build_llm_messages(conversation)

        # Get AI response — reduced tokens for faster inference
        response = await self.llm.chat(messages, temperature=0.7, max_tokens=512)

        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response.content,
            metadata_json={
                "model": response.model,
                "tokens": response.prompt_tokens + response.completion_tokens,
                "duration_s": response.duration_s,
            },
        )
        self.db.add(assistant_msg)
        self.db.commit()
        self.db.refresh(assistant_msg)

        return assistant_msg, conversation

    def build_llm_messages(self, conversation: Conversation) -> list[LLMMessage]:
        """Contexto para el modelo: resumen de lo antiguo + los mensajes recientes completos.

        Evita desbordar la ventana de contexto en conversaciones largas (AD-CMP-04).
        """
        history = self.db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()

        message_count = len([m for m in history if m.role == "user"])
        older, recent = history[:-MAX_CONTEXT_MESSAGES], history[-MAX_CONTEXT_MESSAGES:]
        if older:
            conversation.summary = self._summarize(older)
            self.db.commit()

        system_prompt = self._build_chat_system_prompt(message_count, conversation.summary)
        messages = [LLMMessage(role="system", content=system_prompt)]
        for msg in recent:
            messages.append(LLMMessage(role=msg.role, content=msg.content))
        return messages

    @staticmethod
    def _summarize(messages: list[Message]) -> str:
        """Resumen extractivo de lo que el usuario ya contó (sin llamar al modelo)."""
        summary = " | ".join(m.content[:200] for m in messages if m.role == "user")
        return summary[:MAX_SUMMARY_CHARS]

    def _build_chat_system_prompt(self, message_count: int, existing_summary: str = None) -> str:
        """Build an intelligent system prompt that evolves with the conversation."""
        base = "ADÁN, comité ejecutivo IA. Nivel 1: Descubrimiento del Dolor. Entiende el problema. Español."

        if message_count == 0:
            base += " Saluda y pregunta el problema. Una pregunta a la vez."
        elif message_count <= 2:
            base += " Profundiza: ¿a quién afecta? ¿urgencia? ¿intentos previos?"
        elif message_count <= 5:
            base += " Explora: ¿quién sufre? ¿cuántos? ¿costo sin solución?"
        else:
            base += (
                "\n\nLa conversación está avanzada. "
                "Sintetiza lo que has entendido y pregunta si hay algo más relevante "
                "que no se haya mencionado. Prepárate para cerrar la fase de descubrimiento."
            )

        if existing_summary:
            base += f"\n\nResumen de la conversación hasta ahora: {existing_summary}"

        return base

    # --- Step 3: Board Room ---

    async def run_board_room(self, project: Project, company: Company) -> BoardConsensus:
        """Run the real Board Room with 4 independent agents."""
        # Get conversation context
        card = self.db.query(Card).filter(
            Card.project_id == project.id,
            Card.card_type == "pain_discovery",
        ).first()

        pain_description = ""
        conversation_context = ""

        if card:
            conversation = self.db.query(Conversation).filter(
                Conversation.card_id == card.id,
            ).first()

            if conversation:
                messages = self.db.query(Message).filter(
                    Message.conversation_id == conversation.id,
                ).order_by(Message.created_at).all()

                pain_description = "\n".join([
                    f"{m.role}: {m.content}" for m in messages if m.role == "user"
                ])
                conversation_context = "\n".join([
                    f"{m.role}: {m.content}" for m in messages
                ])

        if not pain_description.strip():
            raise ValueError("No hay descripción del dolor. Inicia una conversación primero.")

        # Run real Board Room
        consensus = await self.board_room.run(pain_description, conversation_context)

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

        return consensus

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
        """Calculate Problem Score and other Level 1 scores."""
        scores = []

        # Problem Score — based on board consensus
        problem_score_value = board_consensus.score
        problem_confidence = board_consensus.confidence

        # Find problem-specific concerns
        problem_concerns = []
        for v in board_consensus.votes:
            problem_concerns.extend(v.key_concerns)

        reasoning = (
            f"Score derivado del análisis del Board Room. "
            f"Decisión: {board_consensus.decision}. "
            f"Confianza promedio: {problem_confidence:.0f}%. "
            f"Preocupaciones: {'; '.join(problem_concerns[:3])}"
        )

        score = self.gemelo.save_score(
            project, "problem", problem_score_value, problem_confidence, reasoning
        )
        scores.append(score)

        return scores

    # --- Step 7: Gate Review ---

    async def run_gate_review(
        self,
        project: Project,
        diagnosis: str,
        board_consensus: BoardConsensus,
        scores: list[Score],
        deliverables: list[str],
    ) -> tuple[GateReviewResult, Decision | None]:
        """Run the DETERMINISTIC Gate Review engine (rules, not LLM).

        Si aprueba, propone cerrar el Nivel: se completa solo cuando el cliente lo aprueba.
        """
        # Build board votes for deterministic evaluation (abstentions are not votes)
        board_votes = [
            {"agent": v.agent, "vote": v.vote, "confidence": v.confidence}
            for v in board_consensus.votes
            if v.vote != "ABSTAIN"
        ]

        scores_data = [
            {"type": s.score_type.value, "value": s.value, "confidence": s.confidence_level}
            for s in scores
        ]

        # Get conversation messages for evaluation
        messages = []
        card = self.db.query(Card).filter(
            Card.project_id == project.id,
            Card.card_type == "pain_discovery",
        ).first()
        if card:
            conv = self.db.query(Conversation).filter(
                Conversation.card_id == card.id,
            ).first()
            if conv:
                msgs = self.db.query(Message).filter(
                    Message.conversation_id == conv.id,
                ).all()
                messages = [{"role": m.role, "content": m.content} for m in msgs]

        # DETERMINISTIC evaluation — no LLM involved in scoring
        result = self.gate_review.evaluate(
            diagnosis=strip_disclaimer(diagnosis),
            board_votes=board_votes,
            scores=scores_data,
            deliverables=deliverables,
            conversation_messages=messages,
        )

        # If approved, propose closing the level; the client decides
        decision = None
        if result.approved:
            decision = self.gemelo.propose_level_completion(
                project, 1, result.overall_score, result.message,
            )

        return result, decision
