"""Auditoría persistente de ejecuciones de herramientas (WO-097, S16)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Index, Integer, String, Text

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class ToolAuditEntry(Base):
    """Registro append-only: cada intento de ejecutar una herramienta deja una fila."""
    __tablename__ = "tef_audit_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tool_id = Column(String(100), nullable=False)
    status = Column(String(30), nullable=False)
    error = Column(Text, nullable=True)
    company_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=False)
    trace_id = Column(String(100), nullable=False)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    __table_args__ = (Index("idx_tef_audit_company_created", "company_id", "created_at"),)
