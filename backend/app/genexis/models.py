"""Lo que construye Genexis y lo que capta: interesados reales que dejan sus datos en la landing de una empresa.

Los datos personales son del fundador (responsable del tratamiento, Ley 1581): se piden con autorización expresa,
solo él los ve y los exporta, y ADÁN solo cuenta cuántos llegan como evidencia de demanda.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Lead(Base):
    __tablename__ = "mvp_leads"

    id = Column(String(36), primary_key=True, default=_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    site = Column(String(80), nullable=False)
    name = Column(String(120), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(40), nullable=True)
    message = Column(Text, nullable=True)
    consent = Column(Boolean, nullable=False, default=False)
    consent_version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False, index=True)
