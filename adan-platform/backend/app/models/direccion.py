"""BP-0006 - AD-005 SS2.5: Direccion y Evidencia."""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import ContratoBaseMixin


class Objetivo(Base, ContratoBaseMixin):
    """AD-005 SS2.5. Entidad 1:N con Empresa. Base de 'Brecha' (AD-FUNC-05) y 'Score por Objetivo' (AD-FUNC-07)."""

    __tablename__ = "objetivos"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    declaracion: Mapped[str] = mapped_column(String)
    horizonte_tiempo: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Meta(Base, ContratoBaseMixin):
    """AD-005 SS2.5. Entidad 1:N con Objetivo (equivalente a Key Result)."""

    __tablename__ = "metas"

    objetivo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("objetivos.id"))
    valor_objetivo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fecha_limite: Mapped[str | None] = mapped_column(String(20), nullable=True)


class Indicador(Base, ContratoBaseMixin):
    """AD-005 SS2.5. Entidad 1:N con Meta. KPI es un valor de tipo, no una entidad distinta."""

    __tablename__ = "indicadores"

    meta_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("metas.id"))
    formula_conceptual: Mapped[str | None] = mapped_column(String, nullable=True)
    frecuencia_medicion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    valor_actual: Mapped[float | None] = mapped_column(nullable=True)


class DecisionNegocio(Base, ContratoBaseMixin):
    """AD-005 SS2.5. Entidad 1:N con Empresa. Distinta de 'Decision' operativa de ADAN (AD-006 SS4).
    Registro de 6 campos cuando el cliente decide distinto a lo recomendado (AD-FUNC-02 SS2.5)."""

    __tablename__ = "decisiones_negocio"

    empresa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    descripcion: Mapped[str] = mapped_column(String)
    opcion_elegida: Mapped[str | None] = mapped_column(String, nullable=True)
    opcion_recomendada: Mapped[str | None] = mapped_column(String, nullable=True)
    nivel_evidencia: Mapped[str | None] = mapped_column(String(50), nullable=True)
    riesgos_asumidos: Mapped[str | None] = mapped_column(String, nullable=True)
    responsabilidad_asumida: Mapped[str | None] = mapped_column(String, nullable=True)
