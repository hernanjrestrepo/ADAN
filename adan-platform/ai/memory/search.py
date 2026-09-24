"""Busqueda semantica real via pgvector (similitud coseno)."""

import uuid

from sqlalchemy.orm import Session

from memory.models import MemoriaSemantica
from models.base import ModelBackend


def semantic_search(
    db: Session,
    model_backend: ModelBackend,
    query: str,
    proyecto_id: uuid.UUID | None = None,
    top_k: int = 5,
) -> list[tuple[MemoriaSemantica, float]]:
    """Devuelve hasta `top_k` fragmentos mas similares a `query`, con su distancia coseno
    (menor = mas similar). `cosine_distance` es el operador nativo de pgvector - sin
    calcular similitud en Python, se delega al indice/scan de Postgres."""
    query_embedding = model_backend.embed(query)

    q = db.query(
        MemoriaSemantica,
        MemoriaSemantica.embedding.cosine_distance(query_embedding).label("distance"),
    )
    if proyecto_id is not None:
        q = q.filter(MemoriaSemantica.proyecto_id == proyecto_id)
    q = q.order_by("distance").limit(top_k)

    return [(row, float(distance)) for row, distance in q.all()]
