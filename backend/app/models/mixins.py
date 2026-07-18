"""Contrato Base (AD-006 SS2) - BP-0007. 7 shared attributes implementing AD-002's 10 rules,
inherited by every one of the 38 entities instead of repeating them per-entity."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class ContratoBaseMixin:
    """AD-002 regla 1.7 (version), 1.5 (nada se pierde -> status, never hard delete),
    1.4 (responsable), 1.1 (evidencia), 1.9 (confidence level cuando aplica)."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | archived, never deleted
    responsible: Mapped[str | None] = mapped_column(String(255), nullable=True)
    evidence_source: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confidence_level: Mapped[float | None] = mapped_column(Float, nullable=True)
