"""Pipeline de ingesta: texto crudo -> chunks -> embeddings reales (Ollama) -> Postgres."""

import uuid

from sqlalchemy.orm import Session

from memory.chunking import chunk_text
from memory.models import MemoriaSemantica
from models.base import ModelBackend


def ingest_text(
    db: Session,
    model_backend: ModelBackend,
    text: str,
    origen: str,
    proyecto_id: uuid.UUID | None = None,
    nodo_id: uuid.UUID | None = None,
) -> list[MemoriaSemantica]:
    """Trocea el texto, genera un embedding real por fragmento, y persiste cada uno.
    Devuelve las filas creadas (sin commit - responsabilidad del llamador, mismo patron
    que el resto del repositorio)."""
    chunks = chunk_text(text)
    rows: list[MemoriaSemantica] = []
    for chunk in chunks:
        embedding = model_backend.embed(chunk)
        row = MemoriaSemantica(
            proyecto_id=proyecto_id,
            nodo_id=nodo_id,
            contenido=chunk,
            origen=origen,
            embedding=embedding,
        )
        db.add(row)
        rows.append(row)
    db.flush()
    return rows
