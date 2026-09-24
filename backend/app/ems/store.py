"""Índice vectorial compartido del EMS.

- **PostgreSQL:** pgvector (`PgVectorStoreProvider`). Los vectores viven en la base, en la
  misma transacción que los chunks (WO-091).
- **SQLite** (desarrollo y pruebas): un índice en memoria compartido por todos los routers,
  que se reconstruye desde la BD la primera vez que se usa (WO-095, B11).

Embeddings: `EMBEDDING_PROVIDER=ollama` usa un modelo real (`nomic-embed-text`); `local`
usa un hash sin red, útil en pruebas. Ambos producen vectores de `EMBEDDING_DIM`.
"""
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import EMBEDDING_DIM, settings
from app.core.database import is_postgres
from app.ems.models import EMSChunk, EMSDocument
from app.ems.pgvector_store import PgVectorStoreProvider
from app.ems.providers import (
    EmbeddingProvider, LocalEmbeddingProvider, LocalVectorStoreProvider, OllamaEmbeddingProvider,
    VectorRecord, VectorStoreProvider,
)


def build_embedding_provider() -> EmbeddingProvider:
    if settings.EMBEDDING_PROVIDER == "ollama":
        return OllamaEmbeddingProvider(settings.OLLAMA_BASE_URL, settings.EMBEDDING_MODEL, EMBEDDING_DIM)
    return LocalEmbeddingProvider(dim=EMBEDDING_DIM)


embedding_provider = build_embedding_provider()
_vector_store = LocalVectorStoreProvider()
_loaded = False


def get_vector_store(db: Session) -> VectorStoreProvider:
    """pgvector con PostgreSQL; con SQLite, el índice en memoria (cargado en el primer uso)."""
    if is_postgres(db.get_bind()):
        return PgVectorStoreProvider(db, embedding_provider.model_name)

    global _loaded
    if not _loaded:
        try:
            rows = (
                db.query(EMSChunk, EMSDocument)
                .join(EMSDocument, EMSChunk.document_id == EMSDocument.id)
                .filter(EMSDocument.status == "processed")
                .all()
            )
        except SQLAlchemyError:
            db.rollback()
            return _vector_store
        vectors = embedding_provider.embed([chunk.content for chunk, _ in rows]) if rows else []
        records = [
            VectorRecord(
                id=chunk.id,
                vector=vector,
                text=chunk.content,
                metadata={
                    "document_id": doc.id,
                    "company_id": chunk.company_id,
                    "chunk_index": chunk.chunk_index,
                    "title": doc.title,
                    "source_type": doc.source_type,
                },
            )
            for (chunk, doc), vector in zip(rows, vectors)
        ]
        _vector_store.upsert(records)
        _loaded = True
    return _vector_store


def describe_providers(db: Session) -> dict:
    """Qué proveedores están activos, para /ems/health."""
    store = get_vector_store(db)
    return {
        "embedding_provider": type(embedding_provider).__name__,
        "embedding_model": embedding_provider.model_name,
        "vector_store": type(store).__name__,
    }
