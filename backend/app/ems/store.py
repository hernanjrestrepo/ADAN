"""Índice vectorial compartido del EMS.

Un solo índice para todos los routers: antes cada uno tenía el suyo, así que lo que se
ingería por /ems no aparecía en la búsqueda vectorial de /agents, /board ni /dka.
Se reconstruye desde la BD la primera vez que se usa, para sobrevivir a reinicios.
WO-091 lo reemplaza por pgvector.
"""
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.ems.models import EMSChunk, EMSDocument
from app.ems.providers import LocalEmbeddingProvider, LocalVectorStoreProvider, VectorRecord

embedding_provider = LocalEmbeddingProvider(dim=128)
_vector_store = LocalVectorStoreProvider()
_loaded = False


def get_vector_store(db: Session) -> LocalVectorStoreProvider:
    """Índice compartido; en el primer uso carga los chunks de documentos procesados."""
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
        records = [
            VectorRecord(
                id=chunk.id,
                vector=embedding_provider.embed_query(chunk.content),
                text=chunk.content,
                metadata={
                    "document_id": doc.id,
                    "company_id": chunk.company_id,
                    "chunk_index": chunk.chunk_index,
                    "title": doc.title,
                    "source_type": doc.source_type,
                },
            )
            for chunk, doc in rows
        ]
        _vector_store.upsert(records)
        _loaded = True
    return _vector_store
