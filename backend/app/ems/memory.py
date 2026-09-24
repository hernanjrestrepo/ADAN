"""
Memory Manager — Gestor central del Enterprise Memory System.

Coordina ingesta, almacenamiento, recuperación y aprendizaje.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.ems.models import (
    EMSDocument, EMSChunk, KnowledgeFact, Correction
)
from app.ems.providers import (
    EmbeddingProvider, VectorStoreProvider
)
from app.ems.ingestion import IngestionPipeline, IngestionResult
from app.ems.retrieval import HybridRetriever, RetrievalResult
from app.ems.chunking import TextChunker


class EnterpriseMemorySystem:
    """
    Sistema de Memoria Empresarial de ADÁN.
    
    Cada empresa tiene su propio espacio de conocimiento,
    separado completamente de las demás.
    """

    def __init__(
        self,
        db: Session,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStoreProvider,
    ):
        self.db = db
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

        # Componentes
        self.ingestion = IngestionPipeline(db, embedding_provider, vector_store)
        self.retriever = HybridRetriever(db, embedding_provider, vector_store)
        self.chunker = TextChunker()

    # ============================================================
    # INGESTA
    # ============================================================

    async def ingest(
        self,
        company_id: str,
        text: str,
        title: str,
        source_type: str = "text",
        source_name: str | None = None,
        metadata: dict | None = None,
    ) -> IngestionResult:
        """Ingresa un documento al sistema de memoria."""
        return await self.ingestion.ingest_text(
            company_id=company_id,
            text=text,
            title=title,
            source_type=source_type,
            source_name=source_name,
            metadata=metadata,
        )

    async def ingest_batch(
        self,
        company_id: str,
        documents: list[dict],
    ) -> list[IngestionResult]:
        """Ingresa múltiples documentos."""
        return await self.ingestion.ingest_batch(company_id, documents)

    # ============================================================
    # RECUPERACIÓN
    # ============================================================

    async def retrieve(
        self,
        company_id: str,
        query: str,
        top_k: int = 5,
    ) -> RetrievalResult:
        """Recupera conocimiento relevante para una query."""
        return await self.retriever.retrieve(
            company_id=company_id,
            query=query,
            top_k=top_k,
        )

    async def retrieve_for_llm(
        self,
        company_id: str,
        query: str,
        max_tokens: int = 4000,
    ) -> str:
        """Recupera contexto formateado para el LLM."""
        result = await self.retrieve(company_id, query)

        # Truncar si excede el presupuesto de tokens
        context = result.context_text
        estimated_tokens = len(context.split())
        if estimated_tokens > max_tokens:
            # Tomar solo los resultados más relevantes
            context = context[:max_tokens * 4]  # ~4 chars por token

        return context

    # ============================================================
    # GESTIÓN DE DOCUMENTOS
    # ============================================================

    def get_document(self, document_id: str) -> EMSDocument | None:
        """Obtiene un documento por ID."""
        return self.ingestion.get_document(document_id)

    def list_documents(
        self,
        company_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[EMSDocument]:
        """Lista documentos de una empresa."""
        return self.ingestion.list_documents(company_id, limit, offset)

    def get_document_chunks(self, document_id: str) -> list[EMSChunk]:
        """Obtiene los chunks de un documento."""
        return self.ingestion.get_document_chunks(document_id)

    def delete_document(self, document_id: str) -> bool:
        """Elimina un documento y sus chunks."""
        doc = self.db.query(EMSDocument).filter(EMSDocument.id == document_id).first()
        if not doc:
            return False

        # Eliminar chunks del vector store
        chunks = self.db.query(EMSChunk).filter(
            EMSChunk.document_id == document_id
        ).all()
        chunk_ids = [c.id for c in chunks]
        if chunk_ids:
            self.vector_store.delete(chunk_ids)

        # Eliminar de BD
        self.db.delete(doc)
        self.db.flush()
        self.db.commit()
        return True

    # ============================================================
    # CONOCIMIENTO (HECHOS)
    # ============================================================

    def add_fact(
        self,
        company_id: str,
        fact_type: str,
        subject: str,
        predicate: str | None = None,
        object_value: str | None = None,
        confidence: float = 1.0,
        source: str | None = None,
        document_id: str | None = None,
    ) -> KnowledgeFact:
        """Agrega un hecho al conocimiento."""
        fact = KnowledgeFact(
            id=str(uuid.uuid4()),
            company_id=company_id,
            document_id=document_id,
            fact_type=fact_type,
            subject=subject,
            predicate=predicate,
            object_value=object_value,
            confidence=confidence,
            source=source,
        )
        self.db.add(fact)
        self.db.flush()
        self.db.commit()
        return fact

    def get_facts(
        self,
        company_id: str,
        fact_type: str | None = None,
        limit: int = 50,
    ) -> list[KnowledgeFact]:
        """Obtiene hechos de una empresa."""
        query = (
            self.db.query(KnowledgeFact)
            .filter(KnowledgeFact.company_id == company_id)
            .filter(KnowledgeFact.is_active == True)
        )
        if fact_type:
            query = query.filter(KnowledgeFact.fact_type == fact_type)
        return query.order_by(KnowledgeFact.created_at.desc()).limit(limit).all()

    # ============================================================
    # APRENDIZAJE (CORRECCIONES)
    # ============================================================

    def record_correction(
        self,
        company_id: str,
        original_text: str,
        corrected_text: str,
        fact_id: str | None = None,
        chunk_id: str | None = None,
        reason: str | None = None,
        created_by: str | None = None,
    ) -> Correction:
        """
        Registra una corrección del usuario.
        
        Cuando el usuario corrige una respuesta:
        1. Registra la corrección
        2. Asocia con el conocimiento original
        3. Ajusta la confianza
        4. Conserva trazabilidad
        """
        correction = Correction(
            id=str(uuid.uuid4()),
            company_id=company_id,
            fact_id=fact_id,
            chunk_id=chunk_id,
            original_text=original_text,
            corrected_text=corrected_text,
            reason=reason,
            created_by=created_by,
        )
        self.db.add(correction)
        self.db.flush()
        self.db.commit()

        # Ajustar confianza del hecho original
        if fact_id:
            fact = self.db.query(KnowledgeFact).filter(
                KnowledgeFact.id == fact_id,
                KnowledgeFact.company_id == company_id,
            ).first()
            if fact:
                fact.confidence = max(0.1, fact.confidence - 0.1)
                fact.updated_at = datetime.now(timezone.utc)

        self.db.flush()
        return correction

    def get_corrections(
        self,
        company_id: str,
        limit: int = 50,
    ) -> list[Correction]:
        """Obtiene correcciones de una empresa."""
        return (
            self.db.query(Correction)
            .filter(Correction.company_id == company_id)
            .order_by(Correction.created_at.desc())
            .limit(limit)
            .all()
        )

    # ============================================================
    # ESTADÍSTICAS
    # ============================================================

    def get_stats(self, company_id: str) -> dict:
        """Obtiene estadísticas del EMS para una empresa."""
        doc_count = (
            self.db.query(EMSDocument)
            .filter(EMSDocument.company_id == company_id)
            .count()
        )
        chunk_count = (
            self.db.query(EMSChunk)
            .filter(EMSChunk.company_id == company_id)
            .count()
        )
        fact_count = (
            self.db.query(KnowledgeFact)
            .filter(KnowledgeFact.company_id == company_id)
            .filter(KnowledgeFact.is_active == True)
            .count()
        )
        correction_count = (
            self.db.query(Correction)
            .filter(Correction.company_id == company_id)
            .count()
        )

        return {
            "documents": doc_count,
            "chunks": chunk_count,
            "facts": fact_count,
            "corrections": correction_count,
            "vector_store_size": self.vector_store.count(),
        }
