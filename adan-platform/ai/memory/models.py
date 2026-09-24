"""Knowledge Graph relacional + memoria semantica - WO-003. BP-0007 (AD-CMP-04, 5 capas
de memoria). Tablas propias de /ai (mismo patron de aislamiento que orchestrator/models.py
- sin FK Python cruzada hacia proyectos.id, la restriccion real vive en Postgres via
schema.sql).

Diferencia con las 37 entidades fijas de AD-005/006 (que viven en /backend): esas son el
esquema RIGIDO del dominio (Empresa, Empleado, Proceso...). El KG es la capa FLEXIBLE para
hechos y relaciones que los Agentes descubren en conversacion y que no encajan en una
columna fija - ej. "el Competidor X subio precios la semana pasada, segun el Empleado Y".
No duplica las 37 entidades - las complementa (Principio de Emergencia: si un hecho ya
tiene una columna fija, va ahi, no al KG)."""

import uuid
from datetime import UTC, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db import Base

EMBEDDING_DIM = 768  # nomic-embed-text


class KGNodo(Base):
    """Un nodo del grafo de conocimiento - una entidad, hecho o concepto descubierto.
    proyecto_id nullable: nodos sin proyecto son conocimiento global (ej. del propio
    blueprint), coherente con la capa Global de AD-CMP-04 SS1."""

    __tablename__ = "kg_nodos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proyecto_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    tipo: Mapped[str] = mapped_column(String(100))  # ej. "hecho", "persona_externa", "senal_mercado"
    nombre: Mapped[str] = mapped_column(String(500))
    atributos: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class KGArista(Base):
    """Una relacion dirigida entre dos nodos del grafo."""

    __tablename__ = "kg_aristas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    origen_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("kg_nodos.id"))
    destino_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("kg_nodos.id"))
    tipo_relacion: Mapped[str] = mapped_column(String(100))
    atributos: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class MemoriaSemantica(Base):
    """Fragmento de texto + su embedding - busqueda semantica real via pgvector.
    Puede o no estar ligado a un KGNodo (nodo_id nullable) - ej. un parrafo de un
    Documento (AD-005) subido por el cliente, chunked e indexado aqui."""

    __tablename__ = "memoria_semantica"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proyecto_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    nodo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    contenido: Mapped[str] = mapped_column(String)
    origen: Mapped[str] = mapped_column(String(100))  # ej. "documento", "conversacion"
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
