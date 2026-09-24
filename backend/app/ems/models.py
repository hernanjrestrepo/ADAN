"""
EMS Models — Modelos de persistencia para el Enterprise Memory System.

Usa EMSBase separado para evitar conflictos con los modelos principales.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Float, Integer, DateTime, JSON, Boolean,
    ForeignKey, Index
)
from sqlalchemy.orm import relationship, DeclarativeBase


class EMSBase(DeclarativeBase):
    """Base separada para modelos EMS."""
    pass


def gen_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class EMSDocument(EMSBase):
    """Documento almacenado en el EMS."""
    __tablename__ = "ems_documents"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    company_id = Column(String(36), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_name = Column(String(500), nullable=True)
    source_url = Column(String(2000), nullable=True)
    content = Column(Text, nullable=True)
    content_type = Column(String(100), nullable=True)
    language = Column(String(10), default="es")
    status = Column(String(20), default="pending")
    version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True)
    parent_version_id = Column(String(36), nullable=True)
    confidence = Column(Float, default=1.0)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    processed_at = Column(DateTime, nullable=True)

    chunks = relationship("EMSChunk", back_populates="document", cascade="all, delete-orphan")
    versions = relationship("EMSVersion", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_ems_doc_company", "company_id"),
        Index("idx_ems_doc_status", "status"),
        Index("idx_ems_doc_source", "source_type"),
    )


class EMSChunk(EMSBase):
    """Chunk de un documento para búsqueda semántica."""
    __tablename__ = "ems_chunks"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    document_id = Column(String(36), ForeignKey("ems_documents.id"), nullable=False)
    company_id = Column(String(36), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=True)
    token_count = Column(Integer, default=0)
    metadata_json = Column(JSON, default=dict)
    embedding_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=utcnow)

    document = relationship("EMSDocument", back_populates="chunks")

    __table_args__ = (
        Index("idx_ems_chunk_doc", "document_id"),
        Index("idx_ems_chunk_company", "company_id"),
    )


class EMSVersion(EMSBase):
    """Historial de versiones de un documento."""
    __tablename__ = "ems_versions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    document_id = Column(String(36), ForeignKey("ems_documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=True)
    change_summary = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=utcnow)
    created_by = Column(String(36), nullable=True)

    document = relationship("EMSDocument", back_populates="versions")


class KnowledgeFact(EMSBase):
    """Hecho extraído del conocimiento."""
    __tablename__ = "ems_facts"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    company_id = Column(String(36), nullable=False, index=True)
    document_id = Column(String(36), nullable=True)
    chunk_id = Column(String(36), nullable=True)
    fact_type = Column(String(50), nullable=False)
    subject = Column(String(500), nullable=False)
    predicate = Column(String(200), nullable=True)
    object_value = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    source = Column(String(500), nullable=True)
    metadata_json = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    superseded_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        Index("idx_ems_fact_company", "company_id"),
        Index("idx_ems_fact_type", "fact_type"),
        Index("idx_ems_fact_subject", "subject"),
    )


class Correction(EMSBase):
    """Corrección del usuario al conocimiento."""
    __tablename__ = "ems_corrections"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    company_id = Column(String(36), nullable=False, index=True)
    fact_id = Column(String(36), ForeignKey("ems_facts.id"), nullable=True)
    chunk_id = Column(String(36), nullable=True)
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=False)
    reason = Column(Text, nullable=True)
    confidence_adjustment = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utcnow)
    created_by = Column(String(36), nullable=True)
