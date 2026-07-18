"""BP-0006 - AD-005 SS2.4: Operacion."""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import ContratoBaseMixin


class Proceso(Base, ContratoBaseMixin):
    """AD-005 SS2.4. Entidad 1:N con Empresa. Destino de 'Automatizar'/'Cambiar procesos' (AD-FUNC-05)."""

    __tablename__ = "procesos"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    nombre: Mapped[str] = mapped_column(String(255))
    objetivo_proceso: Mapped[str | None] = mapped_column(String, nullable=True)
    frecuencia: Mapped[str | None] = mapped_column(String(100), nullable=True)


class Iniciativa(Base, ContratoBaseMixin):
    """AD-005 SS2.4. Entidad 1:N con Empresa. Nombre definitivo - nunca 'Proyecto' (reservado, AD-006 SS4).
    Destino de casi toda Estrategia ejecutada de tipo interno (AD-FUNC-05 SS5/SS7)."""

    __tablename__ = "iniciativas"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    objetivo: Mapped[str | None] = mapped_column(String, nullable=True)
    presupuesto: Mapped[float | None] = mapped_column(nullable=True)


class SucesoEmpresarial(Base, ContratoBaseMixin):
    """AD-005 SS2.4. Entidad 1:N con Empresa. Nombre definitivo - nunca 'Evento' (reservado, AD-006 SS4)."""

    __tablename__ = "sucesos_empresariales"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    naturaleza: Mapped[str | None] = mapped_column(String(50), nullable=True)  # rutinario|critico|fundacional
    descripcion: Mapped[str | None] = mapped_column(String, nullable=True)


class ContratoNegocio(Base, ContratoBaseMixin):
    """AD-005 SS2.4. Entidad N:M con Empresa/Proveedor/Cliente Final. Distinto del Contrato Base tecnico."""

    __tablename__ = "contratos_negocio"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    parte: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vigencia: Mapped[str | None] = mapped_column(String(100), nullable=True)


class Documento(Base, ContratoBaseMixin):
    """AD-005 SS2.4. Entidad 1:N con Empresa. Atributo origen resuelve 'Entregable' sin entidad aparte."""

    __tablename__ = "documentos"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    nombre: Mapped[str] = mapped_column(String(255))
    origen: Mapped[str] = mapped_column(String(50))  # cliente | generado_por_adan
    url_o_contenido: Mapped[str | None] = mapped_column(String, nullable=True)
