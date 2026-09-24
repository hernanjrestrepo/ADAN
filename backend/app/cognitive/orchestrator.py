"""
Cognitive Orchestrator — Orquestador del cerebro cognitivo de ADÁN.

Coordina todos los componentes del sistema cognitivo en un flujo
end-to-end: usuario → memoria → conocimiento → plan → ejecución → respuesta.
"""

import time
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from app.ai.base import LLMAdapter, LLMMessage
from app.models.models import Company, Project, Card, Conversation, Message
from app.services.gemelo_digital import GemeloDigitalService

from app.cognitive.event_bus import EventBus, CognitiveEvent, create_trace_id
from app.cognitive.memory_engine import MemoryEngine, WorkingMemory, ShortTermMemory, LongTermMemory
from app.cognitive.knowledge_engine import KnowledgeEngine, KnowledgeContext
from app.cognitive.planner import Planner, Plan
from app.cognitive.tool_manager import ToolManager
from app.cognitive.decision_engine import DecisionEngine, DecisionJustification


@dataclass
class CognitiveResponse:
    """Respuesta completa del sistema cognitivo."""
    response: str
    trace_id: str
    plan: Plan | None = None
    justification: DecisionJustification | None = None
    knowledge_context: KnowledgeContext | None = None
    events_published: int = 0
    duration_ms: int = 0
    components_used: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


class CognitiveOrchestrator:
    """
    Orquestador principal del sistema cognitivo.
    
    Coordina: Event Bus → Memory → Knowledge → Planner → Tools → 
    Board Room → Decision Engine → Memory Update → Events
    """

    def __init__(self, llm: LLMAdapter, db: Session):
        self.llm = llm
        self.db = db

        # Componentes
        self.event_bus = EventBus(db)
        self.memory_engine = MemoryEngine(db)
        self.knowledge_engine = KnowledgeEngine(db)
        self.planner = Planner(llm)
        self.tool_manager = ToolManager()
        self.decision_engine = DecisionEngine()
        self.gemelo = GemeloDigitalService(db)

    async def process(
        self,
        user_message: str,
        company_id: str,
        user_id: str,
        conversation_id: str | None = None,
    ) -> CognitiveResponse:
        """
        Procesa una solicitud del usuario a través de todo el pipeline cognitivo.
        
        Flujo:
        1. Crear trace_id
        2. Publicar evento de inicio
        3. Cargar memoria
        4. Recuperar conocimiento
        5. Planificar
        6. Ejecutar plan
        7. Evaluar y justificar
        8. Actualizar memorias
        9. Publicar eventos de fin
        """
        start_time = time.time()
        trace_id = create_trace_id()
        events_count = 0
        components_used = []

        # ============================================================
        # PASO 1: Iniciar trace
        # ============================================================
        self._publish_event(
            event_type="cognitive_request_started",
            source="orchestrator",
            trace_id=trace_id,
            company_id=company_id,
            payload={"message": user_message[:200]},
        )
        events_count += 1

        # ============================================================
        # PASO 2: Cargar memoria
        # ============================================================
        components_used.append("memory_engine")

        working_memory = self._load_working_memory(conversation_id)
        short_term = self.memory_engine.get_short_term_memory(company_id, user_id)
        long_term = self.memory_engine.get_long_term_memory(company_id)

        # Agregar mensaje del usuario a Working Memory
        self.memory_engine.update_working_memory(working_memory, "user", user_message)

        self._publish_event(
            event_type="memory_loaded",
            source="memory_engine",
            trace_id=trace_id,
            company_id=company_id,
            payload={
                "working_messages": len(working_memory.messages),
                "short_term_turns": len(short_term.turns),
                "long_term_lessons": len(long_term.lessons),
            },
        )
        events_count += 1

        # ============================================================
        # PASO 3: Recuperar conocimiento
        # ============================================================
        components_used.append("knowledge_engine")

        knowledge_ctx = self.knowledge_engine.get_knowledge_context(company_id)
        knowledge_prompt = self.knowledge_engine.build_knowledge_prompt(knowledge_ctx)

        self._publish_event(
            event_type="knowledge_retrieved",
            source="knowledge_engine",
            trace_id=trace_id,
            company_id=company_id,
            payload={
                "units_count": len(knowledge_ctx.units),
                "has_company": bool(knowledge_ctx.company_info),
                "has_project": bool(knowledge_ctx.project_info),
                "scores_count": len(knowledge_ctx.scores),
                "decisions_count": len(knowledge_ctx.recent_decisions),
            },
        )
        events_count += 1

        # ============================================================
        # PASO 4: Planificar
        # ============================================================
        components_used.append("planner")

        plan = await self.planner.create_plan(user_message, knowledge_prompt)

        self._publish_event(
            event_type="plan_created",
            source="planner",
            trace_id=trace_id,
            company_id=company_id,
            payload={
                "goal": plan.goal[:200],
                "steps_count": len(plan.steps),
                "components": plan.required_components,
                "reasoning": plan.reasoning[:300],
            },
        )
        events_count += 1

        # ============================================================
        # PASO 5: Ejecutar plan
        # ============================================================
        response_text = ""
        board_consensus = None

        for step in plan.steps:
            step_start = time.time()
            step_component = step.component

            try:
                if step_component == "knowledge_engine":
                    # Ya se ejecutó en el paso 3
                    continue

                elif step_component == "board_room":
                    # Ejecutar Board Room (usa LLM internamente)
                    response_text, board_consensus = await self._execute_board_room(
                        knowledge_ctx, knowledge_prompt, trace_id, company_id
                    )
                    components_used.append("board_room")
                    components_used.append("llm")  # Board Room usa LLM

                elif step_component == "llm":
                    # Generar respuesta con LLM
                    response_text = await self._execute_llm_generation(
                        user_message, knowledge_prompt, working_memory, board_consensus, trace_id, company_id
                    )
                    components_used.append("llm")

                elif step_component == "tool_manager":
                    # Ejecutar herramienta (placeholder para WO-004)
                    pass

            except Exception as e:
                self._publish_event(
                    event_type="step_failed",
                    source="orchestrator",
                    trace_id=trace_id,
                    company_id=company_id,
                    payload={
                        "step": step.order,
                        "component": step_component,
                        "error": str(e),
                    },
                )
                events_count += 1

            step_duration = int((time.time() - step_start) * 1000)
            self._publish_event(
                event_type="step_completed",
                source="orchestrator",
                trace_id=trace_id,
                company_id=company_id,
                payload={
                    "step": step.order,
                    "component": step_component,
                    "duration_ms": step_duration,
                },
            )
            events_count += 1

        # ============================================================
        # PASO 6: Evaluar y justificar
        # ============================================================
        components_used.append("decision_engine")

        response_text, justification = self.decision_engine.evaluate_response(
            response=response_text,
            user_message=user_message,
            knowledge_context=knowledge_prompt,
            board_consensus=board_consensus,
        )

        self._publish_event(
            event_type="response_evaluated",
            source="decision_engine",
            trace_id=trace_id,
            company_id=company_id,
            payload={
                "quality_score": justification.confidence,
                "decision": justification.decision,
                "supporting_facts": len(justification.supporting_facts),
                "alternatives": len(justification.alternatives),
            },
        )
        events_count += 1

        # ============================================================
        # PASO 7: Actualizar memorias
        # ============================================================
        # Working Memory
        self.memory_engine.update_working_memory(
            working_memory, "assistant", response_text, "cognitive_system"
        )

        # Short-Term Memory
        self.memory_engine.update_short_term(
            short_term,
            {
                "summary": f"Consulta: {user_message[:100]} → Respuesta generada",
                "timestamp": time.time(),
            },
        )

        # Long-Term Memory (si hay lección)
        if justification.confidence < 0.5:
            self.memory_engine.update_long_term(
                long_term,
                f"Consulta '{user_message[:50]}' tuvo baja confianza ({justification.confidence:.2f}). "
                f"Considerar mejorar contexto o herramientas.",
            )

        self._publish_event(
            event_type="memory_updated",
            source="memory_engine",
            trace_id=trace_id,
            company_id=company_id,
            payload={
                "working_messages": len(working_memory.messages),
                "short_term_turns": len(short_term.turns),
                "long_term_lessons": len(long_term.lessons),
            },
        )
        events_count += 1

        # ============================================================
        # PASO 8: Persistir conversación y mensaje
        # ============================================================
        self._persist_conversation(
            company_id, user_message, response_text, conversation_id, trace_id
        )

        # ============================================================
        # PASO 9: Publicar evento final
        # ============================================================
        duration_ms = int((time.time() - start_time) * 1000)

        self._publish_event(
            event_type="cognitive_request_completed",
            source="orchestrator",
            trace_id=trace_id,
            company_id=company_id,
            payload={
                "duration_ms": duration_ms,
                "events_published": events_count + 1,
                "components_used": list(set(components_used)),
                "quality_score": justification.confidence,
                "response_length": len(response_text),
            },
        )
        events_count += 1

        # ============================================================
        # RETORNAR RESPUESTA
        # ============================================================
        return CognitiveResponse(
            response=response_text,
            trace_id=trace_id,
            plan=plan,
            justification=justification,
            knowledge_context=knowledge_ctx,
            events_published=events_count,
            duration_ms=duration_ms,
            components_used=list(set(components_used)),
            metrics={
                "working_memory_size": len(working_memory.messages),
                "knowledge_units": len(knowledge_ctx.units),
                "plan_steps": len(plan.steps),
                "quality_score": justification.confidence,
            },
        )

    # ================================================================
    # MÉTODOS AUXILIARES
    # ================================================================

    def _load_working_memory(self, conversation_id: str | None) -> WorkingMemory:
        """Carga Working Memory desde conversación o crea nueva."""
        if conversation_id:
            return self.memory_engine.get_working_memory(conversation_id)
        return WorkingMemory(conversation_id=f"new-{int(time.time())}")

    async def _execute_board_room(
        self,
        knowledge_ctx: KnowledgeContext,
        knowledge_prompt: str,
        trace_id: str,
        company_id: str,
    ) -> tuple[str, dict]:
        """Ejecuta el Board Room y retorna consenso."""
        from app.nivel1.board_room import BoardRoom

        board_room = BoardRoom(self.llm)

        # Preparar contexto para Board Room
        pain_description = knowledge_prompt if knowledge_prompt else "Sin contexto disponible"
        conversation_context = f"Empresa: {knowledge_ctx.company_info.get('name', 'desconocida')}"

        try:
            consensus = await board_room.run(pain_description, conversation_context)

            self._publish_event(
                event_type="board_room_completed",
                source="board_room",
                trace_id=trace_id,
                company_id=company_id,
                payload={
                    "consensus": consensus.decision,
                    "score": consensus.score,
                    "confidence": consensus.confidence,
                    "votes_count": len(consensus.votes),
                    "dissent": consensus.dissent,
                },
            )

            # Construir respuesta del Board Room
            votes_summary = []
            for vote in consensus.votes:
                votes_summary.append(
                    f"{vote.agent}: {vote.vote} (confianza: {vote.confidence}%)"
                )

            response = (
                f"**Análisis del Board Room**\n\n"
                f"Consenso: **{consensus.decision}** (Score: {consensus.score}/100, "
                f"Confianza: {consensus.confidence}%)\n\n"
                f"**Votos:**\n" + "\n".join(f"- {v}" for v in votes_summary) + "\n\n"
                f"**Resumen:** {consensus.summary}"
            )

            consensus_dict = {
                "consensus": consensus.decision,
                "score": consensus.score,
                "confidence": consensus.confidence,
                "summary": consensus.summary,
            }

            return response, consensus_dict

        except Exception as e:
            self._publish_event(
                event_type="board_room_failed",
                source="board_room",
                trace_id=trace_id,
                company_id=company_id,
                payload={"error": str(e)},
            )
            return f"Board Room no disponible: {e}", None

    async def _execute_llm_generation(
        self,
        user_message: str,
        knowledge_prompt: str,
        working_memory: WorkingMemory,
        board_consensus: dict | None,
        trace_id: str,
        company_id: str,
    ) -> str:
        """Genera respuesta usando LLM con contexto completo."""
        system_prompt = """Eres ADÁN, un Sistema Operativo Empresarial con inteligencia artificial.
Tu trabajo es analizar empresas y provide insights accionables.

REGLAS:
- Sé directo y específico.
- Basa tu análisis en los datos disponibles.
- Identifica problemas concretos, no genéricos.
- Proporciona justificación para cada afirmación.
- Si no tienes suficiente información, di claramente qué te falta.
- Responde en español."""

        # Construir contexto
        context_parts = []

        if knowledge_prompt:
            context_parts.append(f"CONOCIMIENTO DE LA EMPRESA:\n{knowledge_prompt}")

        if board_consensus:
            context_parts.append(
                f"ANÁLISIS DEL BOARD ROOM:\n"
                f"Consenso: {board_consensus.get('consensus', 'N/A')}\n"
                f"Score: {board_consensus.get('score', 'N/A')}/100\n"
                f"Resumen: {board_consensus.get('summary', 'N/A')}"
            )

        recent_messages = [m for m in working_memory.messages[-6:] if m.get("role") == "user"]
        if recent_messages:
            history = "\n".join(f"- {m['content'][:200]}" for m in recent_messages)
            context_parts.append(f"HISTORIAL RECIENTE:\n{history}")

        full_context = "\n\n".join(context_parts) if context_parts else "Sin contexto disponible"

        user_prompt = f"""CONTEXTO:\n{full_context}\n\nPREGUNTA DEL USUARIO: {user_message}"""

        response = await self.llm.chat(
            messages=[
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt),
            ],
            temperature=0.7,
            max_tokens=1024,
        )

        self._publish_event(
            event_type="llm_response_generated",
            source="llm",
            trace_id=trace_id,
            company_id=company_id,
            payload={
                "model": response.model,
                "tokens": response.prompt_tokens + response.completion_tokens,
                "duration_ms": int(response.duration_s * 1000),
                "response_length": len(response.content),
            },
        )

        return response.content

    def _persist_conversation(
        self,
        company_id: str,
        user_message: str,
        response_text: str,
        conversation_id: str | None,
        trace_id: str,
    ):
        """Persiste la conversación en la BD (flush; el commit lo hace quien llama)."""
        try:
            from app.models.models import CardStatus, Level

            project = self.db.query(Project).filter(
                Project.company_id == company_id
            ).first()
            if not project:
                return

            if conversation_id:
                conversation = self.db.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
            else:
                level = self.db.query(Level).filter(
                    Level.project_id == project.id,
                    Level.status == "active",
                ).first()
                if not level:
                    return

                # La conversación cognitiva vive en su propia Card del Nivel activo
                card = self.db.query(Card).filter(
                    Card.project_id == project.id,
                    Card.level_id == level.id,
                    Card.card_type == "cognitive",
                ).first()
                if not card:
                    card = Card(
                        project_id=project.id,
                        level_id=level.id,
                        title="Conversación con ADÁN",
                        card_type="cognitive",
                        status=CardStatus.ACTIVE,
                    )
                    self.db.add(card)
                    self.db.flush()

                conversation = self.db.query(Conversation).filter(
                    Conversation.card_id == card.id,
                ).order_by(Conversation.created_at.desc()).first()
                if not conversation:
                    conversation = Conversation(
                        card_id=card.id,
                        title="Conversación Cognitiva",
                    )
                    self.db.add(conversation)
                    self.db.flush()

            if not conversation:
                return

            self.db.add(Message(
                conversation_id=conversation.id,
                role="user",
                content=user_message,
                metadata_json={"trace_id": trace_id, "source": "cognitive"},
            ))
            self.db.add(Message(
                conversation_id=conversation.id,
                role="assistant",
                agent_name="cognitive_system",
                content=response_text,
                metadata_json={"trace_id": trace_id, "source": "cognitive"},
            ))
            self.db.flush()
        except Exception:
            self.db.rollback()

    def _publish_event(
        self,
        event_type: str,
        source: str,
        trace_id: str,
        company_id: str,
        payload: dict,
    ):
        """Publica un evento en el Event Bus."""
        event = CognitiveEvent(
            type=event_type,
            source=source,
            trace_id=trace_id,
            company_id=company_id,
            payload=payload,
        )
        self.event_bus.publish(event)
