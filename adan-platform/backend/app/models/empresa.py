"""BP-0006 - AD-005 SS2.1: Identidad y Gobernanza. Empresa es la raiz de todo el modelo."""

import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import ContratoBaseMixin


class Empresa(Base, ContratoBaseMixin):
    """AD-005 SS2.1. Raiz del modelo - Edad y Madurez Organizacional derivan Etapa/Velocidad (SS4)."""

    __tablename__ = "empresas"

    razon_social: Mapped[str] = mapped_column(String(255))
    jurisdiccion: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tipo_societario: Mapped[str | None] = mapped_column(String(100), nullable=True)
    madurez_organizacional: Mapped[float | None] = mapped_column(nullable=True)  # AD-005 SS4, versionado

    marcas: Mapped[list["Marca"]] = relationship(back_populates="empresa")


class NarrativaFundacional(Base, ContratoBaseMixin):
    """AD-005 SS2.1. Entidad 1:1 con Empresa. Ley 1 (Origen) y Ley 9 (Reinvencion)."""

    __tablename__ = "narrativas_fundacionales"

    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empresas.id"), unique=True
    )
    relato_origen: Mapped[str] = mapped_column(String, nullable=True)
    motivacion_fundadora: Mapped[str | None] = mapped_column(String, nullable=True)


class Marca(Base, ContratoBaseMixin):
    """AD-005 SS2.1. Entidad 1:N con Empresa."""

    __tablename__ = "marcas"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    nombre: Mapped[str] = mapped_column(String(255))
    posicionamiento: Mapped[str | None] = mapped_column(String, nullable=True)
    es_intangible: Mapped[bool] = mapped_column(Boolean, default=True)

    empresa: Mapped["Empresa"] = relationship(back_populates="marcas")


class AccionistaInversionista(Base, ContratoBaseMixin):
    """AD-005 SS2.1. Entidad N:M con Empresa. Tambien destino de la Estrategia 'Levantar inversion' (AD-FUNC-05)."""

    __tablename__ = "accionistas_inversionistas"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    nombre: Mapped[str] = mapped_column(String(255))
    tipo_participacion: Mapped[str | None] = mapped_column(String(100), nullable=True)
