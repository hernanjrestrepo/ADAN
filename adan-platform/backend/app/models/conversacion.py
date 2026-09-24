"""BP-0007 - AD-006 SS4: Conversacion, Agente, Tarea."""

import uuid

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import ContratoBaseMixin

agentes_conversaciones = Table(
    "agentes_conversaciones",
    Base.metadata,
    Column("agente_id", UUID(as_uuid=True), ForeignKey("agentes.id"), primary_key=True),
    Column("conversacion_id", UUID(as_uuid=True), ForeignKey("conversaciones.id"), primary_key=True),
)


class Conversacion(Base, ContratoBaseMixin):
    """AD-006 SS4. Sesion de chat dentro de una Card. 1:N con Card. Canal independiente (AD-FUNC-06 SS3.2)."""

    __tablename__ = "conversaciones"

    card_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cards.id"))
    canal: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # texto|voz|documento|audio|video|imagen (AD-FUNC-06 SS3.2)


class Agente(Base, ContratoBaseMixin):
    """AD-006 SS4. Rol interno especializado. N:M con Conversacion."""

    __tablename__ = "agentes"

    rol: Mapped[str] = mapped_column(String(100))  # ej. CEO, CTO, CFO (AD-003 "Agente")


class Tarea(Base, ContratoBaseMixin):
    """AD-006 SS4. Unidad operativa dentro de un Nivel/Card - distinta de Iniciativa (negocio del cliente)."""

    __tablename__ = "tareas"

    nivel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("niveles.id"), nullable=True
    )
    card_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cards.id"), nullable=True
    )
    descripcion: Mapped[str] = mapped_column(String)
    completada: Mapped[bool] = mapped_column(default=False)
