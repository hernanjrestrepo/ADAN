"""BP-0007 - AD-006 SS4: Proyecto, Workspace y la tabla de asociacion Usuario<->Proyecto.

Identidad Progresiva (AD-FUNC-06 SS3.1) NO se modela aqui como columna - es una etiqueta
DERIVADA (mismo patron que Etapa del Ciclo de Vida, AD-005 SS4), calculada en la capa de
servicio a partir de hitos ya existentes (registro, Empresa vinculada, primera Decision de
Negocio, etc.), nunca almacenada."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import ContratoBaseMixin

if TYPE_CHECKING:
    from app.models.nivel import Nivel

usuarios_proyectos = Table(
    "usuarios_proyectos",
    Base.metadata,
    Column("usuario_id", UUID(as_uuid=True), ForeignKey("usuarios.id"), primary_key=True),
    Column("proyecto_id", UUID(as_uuid=True), ForeignKey("proyectos.id"), primary_key=True),
)


class Proyecto(Base, ContratoBaseMixin):
    """AD-006 SS4. El contenedor de software donde ADAN acompana a una Empresa. 1:1 con Empresa."""

    __tablename__ = "proyectos"

    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empresas.id"), unique=True
    )
    usuario_principal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id")
    )  # AD-006 Hallazgo 1 / AD-FUNC-06 SS3.1 "Responsable de Empresa" - relacion 1:N, no flag

    workspace: Mapped["Workspace | None"] = relationship(back_populates="proyecto", uselist=False)
    niveles: Mapped[list["Nivel"]] = relationship(back_populates="proyecto")


class Workspace(Base, ContratoBaseMixin):
    """AD-006 SS4. La interfaz que envuelve un Proyecto. 1:1 con Proyecto."""

    __tablename__ = "workspaces"

    proyecto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("proyectos.id"), unique=True
    )

    proyecto: Mapped["Proyecto"] = relationship(back_populates="workspace")
