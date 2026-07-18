"""BP-0007, BP-0025 - AD-006 SS4: Decision (de ADAN), Score, Evento.

Score: N:1 con Empresa O con Usuario (Usuario Principal) - AD-006 v1.2, cardinalidad
ampliada para cubrir 'Score del Responsable' (antes 'Founder Score', AD-FUNC-07 SS0/SS3),
distinto de 'Venture Score' que es N:1 con Empresa (AD-FUNC-07 SS4). Se modela con dos
FK nullable en vez de una polimorfica generica, para mantener integridad referencial
real en Postgres (mismo patron que Riesgo/Intangible como propiedades transversales)."""

import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import ContratoBaseMixin


class DecisionAdan(Base, ContratoBaseMixin):
    """AD-006 SS4. Registro de una recomendacion aprobada por el cliente (AD-CMP-03).
    Puede originarse en o producir una DecisionNegocio - relacion explicita, no fusion."""

    __tablename__ = "decisiones_adan"

    proyecto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("proyectos.id"))
    decision_negocio_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("decisiones_negocio.id"), nullable=True
    )
    descripcion: Mapped[str] = mapped_column(String)


class Score(Base, ContratoBaseMixin):
    """AD-006 SS4 (v1.2). 8 tipos nombrados en AD-FUNC-07 - ver `tipo`.
    N:1 con Empresa (6 de diagnostico + Venture Score) o con Usuario (Score del Responsable)."""

    __tablename__ = "scores"

    empresa_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=True
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    tipo: Mapped[str] = mapped_column(
        String(50)
    )  # problem|solution|business|product|market|execution|responsable|venture (AD-FUNC-07)
    valor: Mapped[float] = mapped_column(Float)
    # confidence_level ya viene del ContratoBaseMixin - AD-002 regla 1.9, nunca un score separado (AD-FUNC-07 SS6)


class Evento(Base, ContratoBaseMixin):
    """AD-006 SS4. Registro tecnico append-only (timeline). Distinto de SucesoEmpresarial.
    AD-008: toda transicion de estado de Patron A/B/D genera un Evento automaticamente."""

    __tablename__ = "eventos"

    proyecto_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("proyectos.id"))
    suceso_empresarial_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sucesos_empresariales.id"), nullable=True
    )
    tipo: Mapped[str] = mapped_column(String(100))
    payload: Mapped[str | None] = mapped_column(String, nullable=True)
