"""BP-0006 - AD-005 SS2.6: Finanzas."""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import ContratoBaseMixin


class Activo(Base, ContratoBaseMixin):
    """AD-005 SS2.6. Entidad 1:N con Empresa. Liquidez relevante para Ley 6 (Crisis)."""

    __tablename__ = "activos"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    tipo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    valor: Mapped[float | None] = mapped_column(nullable=True)
    liquidez: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Pasivo(Base, ContratoBaseMixin):
    """AD-005 SS2.6. Entidad 1:N con Empresa."""

    __tablename__ = "pasivos"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    tipo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    monto: Mapped[float | None] = mapped_column(nullable=True)
    plazo: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Ingreso(Base, ContratoBaseMixin):
    """AD-005 SS2.6. Entidad 1:N con Empresa."""

    __tablename__ = "ingresos"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    fuente: Mapped[str | None] = mapped_column(String(255), nullable=True)
    monto: Mapped[float | None] = mapped_column(nullable=True)
    periodicidad: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Gasto(Base, ContratoBaseMixin):
    """AD-005 SS2.6. Entidad 1:N con Empresa."""

    __tablename__ = "gastos"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    categoria: Mapped[str | None] = mapped_column(String(100), nullable=True)
    monto: Mapped[float | None] = mapped_column(nullable=True)
    periodicidad: Mapped[str | None] = mapped_column(String(50), nullable=True)
