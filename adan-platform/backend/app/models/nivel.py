"""BP-0007, BP-0016 - AD-006 SS4 + AD-FUNC-01: Nivel y Card.

Los 7 Niveles quedaron congelados definitivamente por AD-FUNC-01 - este modulo no
reabre esa numeracion. numero (1-7) es Decision de Diseno solo en el sentido de que
AD-ARQ-10 fija los umbrales de avance (Patron B, AD-CMP-01), nunca el numero de Niveles."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import ContratoBaseMixin

if TYPE_CHECKING:
    from app.models.proyecto import Proyecto


class Nivel(Base, ContratoBaseMixin):
    """AD-006 SS4. Etapa del acompanamiento. 1:N con Proyecto. Patron B (Progreso Secuencial, AD-CMP-01)."""

    __tablename__ = "niveles"

    proyecto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("proyectos.id"))
    numero: Mapped[int] = mapped_column(Integer)  # 1-7, AD-FUNC-01, congelado definitivamente
    nombre: Mapped[str] = mapped_column(String(255))
    completado: Mapped[bool] = mapped_column(default=False)

    proyecto: Mapped["Proyecto"] = relationship(back_populates="niveles")
    cards: Mapped[list["Card"]] = relationship(back_populates="nivel")


class Card(Base, ContratoBaseMixin):
    """AD-006 SS4. Unidad de trabajo dentro de un Nivel. 1:N con Nivel."""

    __tablename__ = "cards"

    nivel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("niveles.id"))
    nombre: Mapped[str] = mapped_column(String(255))

    nivel: Mapped["Nivel"] = relationship(back_populates="cards")
