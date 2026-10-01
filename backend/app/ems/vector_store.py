"""Vector store persistente del EMS sobre la base de datos (WO-091).

- PostgreSQL: columna `vector` de pgvector y ordenamiento por distancia
  coseno (`<=>`) en la propia base.
- SQLite: vectores en JSON y similitud coseno calculada en Python sobre los
  registros de la empresa (suficiente para desarrollo y tests).

Opera sobre la sesión de la request: `upsert`/`delete` no hacen commit, la
transacción la cierra quien llama (IngestionPipeline / EnterpriseMemorySystem).
"""
from __future__ import annotations

import math

from sqlalchemy import Float, bindparam, func
from sqlalchemy.orm import Session

from app.core.types import EmbeddingVector
from app.ems.models import EMSEmbedding
from app.ems.providers import SearchResult, VectorRecord, VectorStoreProvider


class SQLVectorStoreProvider(VectorStoreProvider):
    """Vector store respaldado por la tabla `ems_embeddings`."""

    def __init__(self, db: Session):
        self.db = db

    @property
    def _is_postgres(self) -> bool:
        return self.db.get_bind().dialect.name == "postgresql"

    def upsert(self, records: list[VectorRecord]) -> int:
        for record in records:
            self.db.merge(EMSEmbedding(
                id=record.id,
                company_id=str(record.metadata.get("company_id", "")),
                document_id=record.metadata.get("document_id"),
                content=record.text or "",
                metadata_json=dict(record.metadata),
                dim=len(record.vector),
                embedding=list(record.vector),
            ))
        self.db.flush()
        return len(records)

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[SearchResult]:
        filter_metadata = dict(filter_metadata or {})
        query = self.db.query(EMSEmbedding).filter(EMSEmbedding.dim == len(query_vector))
        company_id = filter_metadata.pop("company_id", None)
        if company_id is not None:
            query = query.filter(EMSEmbedding.company_id == company_id)

        if self._is_postgres and not filter_metadata:
            distance = EMSEmbedding.embedding.op("<=>", return_type=Float)(
                bindparam("query_vector", list(query_vector), type_=EmbeddingVector())
            )
            rows = query.add_columns(distance).order_by(distance).limit(top_k).all()
            return [
                SearchResult(
                    id=row.id,
                    score=0.0 if dist is None or math.isnan(dist) else 1.0 - dist,
                    text=row.content,
                    metadata=row.metadata_json or {},
                )
                for row, dist in rows
            ]

        results = []
        for row in query.all():
            metadata = row.metadata_json or {}
            if any(metadata.get(k) != v for k, v in filter_metadata.items()):
                continue
            results.append(SearchResult(
                id=row.id,
                score=_cosine_similarity(query_vector, row.embedding),
                text=row.content,
                metadata=metadata,
            ))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def delete(self, ids: list[str]) -> int:
        if not ids:
            return 0
        deleted = (
            self.db.query(EMSEmbedding)
            .filter(EMSEmbedding.id.in_(ids))
            .delete(synchronize_session=False)
        )
        self.db.flush()
        return deleted

    def count(self, company_id: str | None = None) -> int:
        query = self.db.query(func.count(EMSEmbedding.id))
        if company_id is not None:
            query = query.filter(EMSEmbedding.company_id == company_id)
        return query.scalar() or 0


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
