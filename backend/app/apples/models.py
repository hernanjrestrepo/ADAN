"""@pples: la moneda de ADÁN (1 @pple = USD 1). Se compran con dinero real y solo se gastan dentro de ADÁN y Paradixe;
nunca se convierten de vuelta en dinero. El saldo sale de sumar un libro de movimientos que no se borra."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


MOVEMENT_KINDS = ("compra", "nivel", "referido", "bienvenida", "ajuste")
PURCHASE_STATES = ("pendiente", "aprobada", "rechazada")


class ReferralProfile(Base):
    """Cada cuenta tiene su código de invitación. Quién la invitó (el nivel 1 de su red) se fija al registrarse y no
    cambia: la red no se reacomoda."""
    __tablename__ = "apple_referrals"

    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    code = Column(String(8), unique=True, index=True, nullable=False)
    sponsor_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)


class AppleMovement(Base):
    """Una entrada (positiva) o salida (negativa) de @pples. `reference` + `kind` + `user_id` es único: un pago o una
    comisión nunca se cuenta dos veces."""
    __tablename__ = "apple_movements"
    __table_args__ = (
        UniqueConstraint("kind", "reference", "user_id", name="uq_apple_movement_once"),
        Index("idx_apple_movements_user", "user_id", "created_at"),
    )

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    kind = Column(String(12), nullable=False)
    amount = Column(Numeric(14, 3), nullable=False)
    reference = Column(String(80), nullable=False)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    level_number = Column(Integer, nullable=True)
    depth = Column(Integer, nullable=True)  # en comisiones: 1 = quien invitó directamente a quien pagó
    source_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    detail = Column(String(200), nullable=False, default="")
    created_at = Column(DateTime, default=_now, nullable=False)


class ApplePurchase(Base):
    """Compra de @pples con dinero real a través de la pasarela (Wompi, o el simulador mientras no haya llaves)."""
    __tablename__ = "apple_purchases"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    apples = Column(Integer, nullable=False)
    amount_cop = Column(Integer, nullable=False)
    trm = Column(Integer, nullable=False)
    provider = Column(String(20), nullable=False)
    external_id = Column(String(80), nullable=True)
    status = Column(String(12), nullable=False, default="pendiente")
    checkout_url = Column(String(1000), nullable=False, default="")
    created_at = Column(DateTime, default=_now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)


class LevelUnlock(Base):
    """Un Nivel de una empresa pagado con @pples. Se paga una sola vez."""
    __tablename__ = "apple_level_unlocks"
    __table_args__ = (UniqueConstraint("company_id", "level_number", name="uq_apple_level_unlock"),)

    id = Column(String(36), primary_key=True, default=_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    level_number = Column(Integer, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    apples = Column(Numeric(14, 3), nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
