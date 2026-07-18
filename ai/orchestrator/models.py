"""Registro de ejecuciones - tabla propia de /ai, en el mismo Postgres fisico que /backend
pero SIN importar app.models (Plan Maestro SS3.2: sin acoplamiento directo entre celulas
fuera de contratos). El contrato es el esquema de esta tabla, documentado en
contracts/events/agent_execution.md. FK por nombre de tabla (proyectos.id) - referencia
real de integridad en Postgres sin import de Python."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class EjecucionAgente(Base):
    """Una corrida de un Agente. Analogo de proposito a AD-006 SS4 'Decision (de ADAN)'
    pero a nivel de infraestructura de ejecucion, no de dominio de producto - vive en /ai,
    no es una entidad del blueprint (AD-005/006).

    proyecto_id NO declara ForeignKey() aqui a proposito: la restriccion real ya existe en
    Postgres (aplicada via schema.sql), pero declararla tambien en este ORM hace que
    SQLAlchemy intente resolver la tabla 'proyectos' dentro del Base de /ai (que no la
    conoce, a proposito - Plan Maestro SS3.2) y falla al hacer flush/create_all. La
    integridad referencial vive en la base de datos, no en este mapeo Python."""

    __tablename__ = "ejecuciones_agente"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[str] = mapped_column(String(100))
    proyecto_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    user_input: Mapped[str] = mapped_column(String)
    final_output: Mapped[str | None] = mapped_column(String, nullable=True)
    transcript: Mapped[list | None] = mapped_column(JSONB, nullable=True)  # lista de StepRecord serializados
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
