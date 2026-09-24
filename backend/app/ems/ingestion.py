"""
Ingestion Pipeline — Procesamiento de documentos de entrada.

Pipeline: Documento → Extracción → Limpieza → Chunking → Clasificación → Metadata → Embeddings → Vector Store → Knowledge Graph → Indexación
"""

import uuid
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from app.ems.models import EMSDocument, EMSChunk, EMSVersion
from app.ems.chunking import TextChunker, Chunk
from app.ems.providers import (
    EmbeddingProvider, VectorStoreProvider, VectorRecord
)


@dataclass
class IngestionResult:
    """Resultado de la ingesta de un documento."""
    document_id: str
    status: str  # success, error
    chunks_created: int
    embeddings_generated: int
    vector_records_upserted: int
    duration_ms: int
    error: str | None = None
    metadata: dict = field(default_factory=dict)


class IngestionPipeline:
    """
    Pipeline de ingesta de documentos.
    
    Flujo:
    1. Recibir documento
    2. Extraer contenido (si es necesario)
    3. Limpiar texto
    4. Dividir en chunks
    5. Generar embeddings
    6. Almacenar en vector store
    7. Registrar en BD
    """

    def __init__(
        self,
        db: Session,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStoreProvider,
        chunker: TextChunker | None = None,
    ):
        self.db = db
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.chunker = chunker or TextChunker()

    async def ingest_text(
        self,
        company_id: str,
        text: str,
        title: str,
        source_type: str = "text",
        source_name: str | None = None,
        metadata: dict | None = None,
    ) -> IngestionResult:
        """Ingresa texto plano al sistema."""
        start_time = datetime.now(timezone.utc)

        try:
            # 1. Crear registro de documento
            doc = EMSDocument(
                id=str(uuid.uuid4()),
                company_id=company_id,
                title=title,
                source_type=source_type,
                source_name=source_name,
                content=text,
                content_type="text/plain",
                status="processing",
                metadata_json=metadata or {},
            )
            self.db.add(doc)
            self.db.flush()

            # 2. Chunking
            chunks = self.chunker.chunk(text, metadata={"document_id": doc.id})

            # 3. Guardar chunks en BD
            db_chunks = []
            for chunk in chunks:
                db_chunk = EMSChunk(
                    id=str(uuid.uuid4()),
                    document_id=doc.id,
                    company_id=company_id,
                    chunk_index=chunk.index,
                    content=chunk.content,
                    content_hash=chunk.content_hash,
                    token_count=chunk.token_count,
                    metadata_json=chunk.metadata,
                )
                self.db.add(db_chunk)
                db_chunks.append(db_chunk)
            self.db.flush()

            # 4. Generar embeddings
            texts_to_embed = [c.content for c in chunks]
            embeddings = self.embedding_provider.embed(texts_to_embed)

            # 5. Crear registros para vector store
            vector_records = []
            for i, (db_chunk, embedding) in enumerate(zip(db_chunks, embeddings)):
                record = VectorRecord(
                    id=db_chunk.id,
                    vector=embedding,
                    text=db_chunk.content,
                    metadata={
                        "document_id": doc.id,
                        "company_id": company_id,
                        "chunk_index": db_chunk.chunk_index,
                        "title": title,
                        "source_type": source_type,
                    },
                )
                vector_records.append(record)
                db_chunk.embedding_id = db_chunk.id

            # 6. Upsert en vector store
            upserted = self.vector_store.upsert(vector_records)

            # 7. Actualizar documento
            doc.status = "processed"
            doc.processed_at = datetime.now(timezone.utc)

            # 8. Crear versión
            version = EMSVersion(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                version_number=1,
                content_hash=hashlib.sha256(text.encode()).hexdigest()[:16],
                change_summary="Versión inicial",
                confidence=1.0,
            )
            self.db.add(version)

            self.db.flush()
            self.db.commit()

            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

            return IngestionResult(
                document_id=doc.id,
                status="success",
                chunks_created=len(chunks),
                embeddings_generated=len(embeddings),
                vector_records_upserted=upserted,
                duration_ms=duration_ms,
                metadata={
                    "title": title,
                    "source_type": source_type,
                    "chunk_size": self.chunker.chunk_size,
                },
            )

        except Exception as e:
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            return IngestionResult(
                document_id="",
                status="error",
                chunks_created=0,
                embeddings_generated=0,
                vector_records_upserted=0,
                duration_ms=duration_ms,
                error=str(e),
            )

    async def ingest_batch(
        self,
        company_id: str,
        documents: list[dict],
    ) -> list[IngestionResult]:
        """Ingresa múltiples documentos."""
        results = []
        for doc in documents:
            result = await self.ingest_text(
                company_id=company_id,
                text=doc.get("text", ""),
                title=doc.get("title", "Sin título"),
                source_type=doc.get("source_type", "text"),
                source_name=doc.get("source_name"),
                metadata=doc.get("metadata"),
            )
            results.append(result)
        return results

    def get_document(self, document_id: str) -> EMSDocument | None:
        """Obtiene un documento por ID."""
        return self.db.query(EMSDocument).filter(EMSDocument.id == document_id).first()

    def list_documents(
        self,
        company_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[EMSDocument]:
        """Lista documentos de una empresa."""
        return (
            self.db.query(EMSDocument)
            .filter(EMSDocument.company_id == company_id)
            .order_by(EMSDocument.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_document_chunks(self, document_id: str) -> list[EMSChunk]:
        """Obtiene los chunks de un documento."""
        return (
            self.db.query(EMSChunk)
            .filter(EMSChunk.document_id == document_id)
            .order_by(EMSChunk.chunk_index)
            .all()
        )
