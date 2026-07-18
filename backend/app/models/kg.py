"""Espejo de lectura/escritura de las tablas del Knowledge Graph, propiedad real de /ai
(ver ai/memory/models.py y ai/memory/schema.sql). Mismo patron que ejecucion_agente.py -
Base propio, sin importar el ORM de /ai. NO registrado en app/models/__init__.py (Alembic
no gestiona estas tablas, las migra /ai)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class KGNodoBackend(Base):
    __tablename__ = "kg_nodos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proyecto_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    tipo: Mapped[str] = mapped_column(String(100))
    nombre: Mapped[str] = mapped_column(String(500))
    atributos: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class KGAristaBackend(Base):
    __tablename__ = "kg_aristas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    origen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    destino_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    tipo_relacion: Mapped[str] = mapped_column(String(100))
    atributos: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
