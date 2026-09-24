"""Almacén vectorial del EMS sobre PostgreSQL + pgvector (WO-091).

Los vectores viven en `ems_chunk_embeddings`, en la misma transacción que los chunks,
así que sobreviven a reinicios y los ven todos los routers. La búsqueda usa la distancia
coseno nativa de pgvector y excluye documentos archivados.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ems.models import EMSChunk, EMSChunkEmbedding, EMSDocument
from app.ems.providers import SearchResult, VectorRecord, VectorStoreProvider

# Claves de metadata por las que se puede filtrar, y su columna
_FILTERS = {
    "company_id": EMSChunkEmbedding.company_id,
    "document_id": EMSChunkEmbedding.document_id,
}


class PgVectorStoreProvider(VectorStoreProvider):
    def __init__(self, db: Session, embedding_model: str):
        self.db = db
        self.embedding_model = embedding_model

    def upsert(self, records: list[VectorRecord]) -> int:
        for record in records:
            self.db.merge(EMSChunkEmbedding(
                chunk_id=record.id,
                document_id=record.metadata["document_id"],
                company_id=record.metadata["company_id"],
                embedding=record.vector,
                embedding_model=self.embedding_model,
            ))
        self.db.flush()
        return len(records)

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[SearchResult]:
        distance = EMSChunkEmbedding.embedding.cosine_distance(query_vector)
        stmt = (
            select(EMSChunk, EMSDocument, distance.label("distance"))
            .select_from(EMSChunkEmbedding)
            .join(EMSChunk, EMSChunk.id == EMSChunkEmbedding.chunk_id)
            .join(EMSDocument, EMSDocument.id == EMSChunkEmbedding.document_id)
            .where(EMSDocument.status != "archived")
            # Vectores de otro modelo no son comparables con la consulta
            .where(EMSChunkEmbedding.embedding_model == self.embedding_model)
        )
        for key, value in (filter_metadata or {}).items():
            if key not in _FILTERS:
                raise ValueError(f"Filtro no soportado por pgvector: {key}")
            stmt = stmt.where(_FILTERS[key] == value)
        stmt = stmt.order_by(distance).limit(top_k)

        return [
            SearchResult(
                id=chunk.id,
                score=1.0 - float(dist),
                text=chunk.content,
                metadata={
                    "document_id": doc.id,
                    "company_id": chunk.company_id,
                    "chunk_index": chunk.chunk_index,
                    "title": doc.title,
                    "source_type": doc.source_type,
                },
            )
            for chunk, doc, dist in self.db.execute(stmt).all()
        ]

    def delete(self, ids: list[str]) -> int:
        if not ids:
            return 0
        deleted = (
            self.db.query(EMSChunkEmbedding)
            .filter(EMSChunkEmbedding.chunk_id.in_(ids))
            .delete(synchronize_session=False)
        )
        self.db.flush()
        return deleted

    def count(self, filter_metadata: dict | None = None) -> int:
        stmt = select(func.count()).select_from(EMSChunkEmbedding)
        for key, value in (filter_metadata or {}).items():
            if key not in _FILTERS:
                raise ValueError(f"Filtro no soportado por pgvector: {key}")
            stmt = stmt.where(_FILTERS[key] == value)
        return self.db.execute(stmt).scalar_one()
