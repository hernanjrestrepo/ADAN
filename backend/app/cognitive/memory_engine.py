"""
Memory Engine — Gestión de memoria del sistema cognitivo.

Implementa Working Memory, Short-Term Memory y Long-Term Memory
para el vertical slice de WO-003.
"""

import json
from datetime import datetime, timezone
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from app.models.models import Conversation, Message, Project


@dataclass
class WorkingMemory:
    """Memoria de trabajo — contexto activo de una request."""
    conversation_id: str
    messages: list[dict] = field(default_factory=list)
    summary: str = ""
    attention_focus: list[str] = field(default_factory=list)
    tool_results: list[dict] = field(default_factory=list)
    turn_count: int = 0


@dataclass
class ShortTermMemory:
    """Memoria a corto plazo — contexto de una sesión."""
    session_id: str
    user_id: str
    company_id: str
    turns: list[dict] = field(default_factory=list)
    decisions_made: list[dict] = field(default_factory=list)
    key_discoveries: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    compressed_summary: str | None = None


@dataclass
class LongTermMemory:
    """Memoria a largo plazo — conocimiento acumulado."""
    company_id: str
    project_snapshots: list[dict] = field(default_factory=list)
    decision_history: list[dict] = field(default_factory=list)
    user_preferences: dict = field(default_factory=dict)
    patterns: list[dict] = field(default_factory=list)
    lessons: list[str] = field(default_factory=list)
    version: int = 1


class MemoryEngine:
    """
    Motor de memoria que gestiona los 3 niveles de memoria
    para el vertical slice.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_working_memory(self, conversation_id: str) -> WorkingMemory:
        """Carga Working Memory desde la conversación existente."""
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            return WorkingMemory(conversation_id=conversation_id)

        messages = []
        for msg in conversation.messages[-20:]:  # Últimos 20 mensajes
            messages.append({
                "role": msg.role,
                "content": msg.content,
                "agent_name": msg.agent_name,
                "timestamp": msg.created_at.isoformat() if msg.created_at else None,
            })

        return WorkingMemory(
            conversation_id=conversation_id,
            messages=messages,
            summary=conversation.summary or "",
            turn_count=len(messages),
        )

    def get_short_term_memory(self, company_id: str, user_id: str) -> ShortTermMemory:
        """Carga Short-Term Memory (resúmenes de sesiones recientes)."""
        # Obtener las últimas 5 conversaciones con resumen
        conversations = (
            self.db.query(Conversation)
            .join(Message)
            .filter(Message.conversation_id == Conversation.id)
            .distinct()
            .order_by(Conversation.created_at.desc())
            .limit(5)
            .all()
        )

        turns = []
        for conv in conversations:
            if conv.summary:
                turns.append({
                    "conversation_id": str(conv.id),
                    "summary": conv.summary,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                })

        return ShortTermMemory(
            session_id=f"session-{company_id}",
            user_id=user_id,
            company_id=company_id,
            turns=turns,
        )

    def get_long_term_memory(self, company_id: str) -> LongTermMemory:
        """Carga Long-Term Memory (conocimiento acumulado)."""
        # Por ahora, retorna memoria vacía con estructura correcta
        # En WO-004 se implementará con persistencia completa
        return LongTermMemory(company_id=company_id)

    def update_working_memory(
        self, working: WorkingMemory, role: str, content: str, agent_name: str | None = None
    ):
        """Agrega un mensaje a Working Memory."""
        working.messages.append({
            "role": role,
            "content": content,
            "agent_name": agent_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        working.turn_count += 1

    def update_short_term(
        self, short_term: ShortTermMemory, turn_summary: dict
    ):
        """Agrega un resumen de turno a Short-Term Memory."""
        short_term.turns.append(turn_summary)

    def update_long_term(
        self, long_term: LongTermMemory, lesson: str
    ):
        """Agrega una lección a Long-Term Memory."""
        long_term.lessons.append(lesson)

    def build_context_for_llm(
        self, working: WorkingMemory, short_term: ShortTermMemory, long_term: LongTermMemory
    ) -> str:
        """Construye el contexto optimizado para el LLM."""
        parts = []

        # 1. Resumen de sesión (si existe)
        if short_term.turns:
            recent_summaries = [t.get("summary", "") for t in short_term.turns[-3:] if t.get("summary")]
            if recent_summaries:
                parts.append(f"Contexto de sesiones anteriores: {' | '.join(recent_summaries)}")

        # 2. Lecciones de Long-Term
        if long_term.lessons:
            parts.append(f"Lecciones aprendidas: {'; '.join(long_term.lessons[-3:])}")

        # 3. Mensajes recientes de Working Memory
        recent = working.messages[-10:]
        for msg in recent:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                parts.append(f"Usuario: {content}")
            elif role == "assistant":
                parts.append(f"ADÁN: {content}")

        return "\n".join(parts)

    def save_conversation_summary(self, conversation_id: str, summary: str):
        """Guarda el resumen de una conversación."""
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if conversation:
            conversation.summary = summary
            self.db.flush()
