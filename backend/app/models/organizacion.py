"""BP-0006 - AD-005 SS2.2: Estructura Organizacional y Personas."""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import ContratoBaseMixin


class Departamento(Base, ContratoBaseMixin):
    """AD-005 SS2.2. Entidad 1:N con Empresa, auto-relacionable (jerarquia)."""

    __tablename__ = "departamentos"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    nombre: Mapped[str] = mapped_column(String(255))
    departamento_padre_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departamentos.id"), nullable=True
    )


class Cargo(Base, ContratoBaseMixin):
    """AD-005 SS2.2. Entidad 1:N con Departamento."""

    __tablename__ = "cargos"

    departamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departamentos.id")
    )
    nombre: Mapped[str] = mapped_column(String(255))
    nivel_jerarquico: Mapped[int | None] = mapped_column(nullable=True)
    reporta_a_cargo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cargos.id"), nullable=True
    )


class RolFuncional(Base, ContratoBaseMixin):
    """AD-005 SS2.2. Entidad N:M con Cargo."""

    __tablename__ = "roles_funcionales"

    nombre: Mapped[str] = mapped_column(String(255))
    descripcion: Mapped[str | None] = mapped_column(String, nullable=True)


class Empleado(Base, ContratoBaseMixin):
    """AD-005 SS2.2. Entidad 1:N con Empresa. Historial de Cargos via Contrato Base (versionado)."""

    __tablename__ = "empleados"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    cargo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cargos.id"), nullable=True
    )
    nombre: Mapped[str] = mapped_column(String(255))
    fecha_ingreso: Mapped[str | None] = mapped_column(String(20), nullable=True)
