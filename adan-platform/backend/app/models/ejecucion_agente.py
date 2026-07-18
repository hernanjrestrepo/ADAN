"""Modelo de LECTURA de la tabla ejecuciones_agente, propiedad real de /ai (ver
ai/orchestrator/models.py y contracts/events/agent_execution.md). /backend NO importa el
ORM de /ai (Plan Maestro SS3.2) - mapea la misma tabla fisica con su propio Base, siguiendo
el contrato documentado. Solo se usa para lectura (GET /agents/runs/{id}); la escritura es
responsabilidad exclusiva del worker de /ai."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class EjecucionAgenteLectura(Base):
    __tablename__ = "ejecuciones_agente"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(100))
    proyecto_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20))
    user_input: Mapped[str] = mapped_column(String)
    final_output: Mapped[str | None] = mapped_column(String, nullable=True)
    transcript: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
