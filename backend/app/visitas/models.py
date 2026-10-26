"""Visitas a ADÁN: cada página que se abre, para el mapa y las cifras de la consola (como en Xmart Travel).

Sin datos personales: el país lo pone Cloudflare (CF-IPCountry) y el visitante es un resumen (hash) de la IP y el
navegador que cambia cada día, así que no se puede seguir a nadie de un día a otro.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Visit(Base):
    __tablename__ = "visits"

    id = Column(String(36), primary_key=True, default=_uuid)
    created_at = Column(DateTime, default=_now, nullable=False, index=True)
    path = Column(String(200), nullable=False)
    referrer = Column(String(120), nullable=True)
    country = Column(String(2), nullable=True, index=True)
    visitor = Column(String(24), nullable=False, index=True)
    mobile = Column(Boolean, default=False, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    __table_args__ = (Index("ix_visits_created_country", "created_at", "country"),)
