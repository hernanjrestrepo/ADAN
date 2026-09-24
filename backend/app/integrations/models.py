"""Conexiones de integraciones por empresa, con credenciales cifradas (WO-097, S13)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class IntegrationConnection(Base):
    """Un conector conectado por una empresa. Las credenciales nunca salen de aquí sin cifrar."""
    __tablename__ = "integration_connections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    connector_id = Column(String(50), nullable=False)
    credentials_encrypted = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="connected")  # connected, disconnected
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (UniqueConstraint("company_id", "connector_id", name="uq_integration_company_connector"),)
