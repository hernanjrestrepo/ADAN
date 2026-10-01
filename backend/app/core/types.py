"""Tipos SQLAlchemy portables entre PostgreSQL y SQLite."""
from __future__ import annotations

from sqlalchemy import JSON
from sqlalchemy.types import TypeDecorator


class EmbeddingVector(TypeDecorator):
    """Vector de embeddings: `vector` de pgvector en PostgreSQL, JSON en SQLite.

    La columna no fija dimensión, así que se puede cambiar de proveedor de
    embeddings sin migrar; cada fila guarda su `dim` para filtrar búsquedas.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector())
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return [float(x) for x in value]

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return [float(x) for x in value]
