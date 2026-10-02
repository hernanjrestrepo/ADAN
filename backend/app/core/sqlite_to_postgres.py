"""Migración de datos de SQLite a PostgreSQL (WO-091).

    cd backend
    python -m app.core.sqlite_to_postgres --from sqlite:///data/adan.db \\
        --to postgresql://adan:clave@localhost:5432/adan

1. Crea el esquema en el destino con las migraciones de Alembic.
2. Exige que el destino esté vacío: nunca mezcla datos.
3. Copia tabla por tabla, en orden de claves foráneas, usando los tipos del modelo
   (fechas, JSON, enums y booleanos se convierten solos).
4. Recalcula los embeddings de los chunks en pgvector (SQLite no los guardaba).

No modifica el archivo SQLite de origen.
"""
from __future__ import annotations

import argparse
import logging

from sqlalchemy import func, inspect, select
from sqlalchemy.orm import Session

from app.core.config import normalize_database_url
from app.core.database import Base, import_all_models, make_engine
from app.core.migrations import run_migrations

logger = logging.getLogger(__name__)

BATCH_SIZE = 500
# Derivados: se recalculan en el destino, no se copian
SKIP_TABLES = {"ems_chunk_embeddings"}
# Catálogos que siembran las migraciones (WO-098): se fusionan por su clave natural en lugar
# de exigir que el destino esté vacío; las referencias a ellos se traducen a los ids del destino
CATALOG_TABLES = {"agents": "code"}
CATALOG_REFERENCES = {"conversation_agents": {"agent_id": "agents"}}


def migrate(source_url: str, target_url: str, reindex: bool = True) -> dict[str, int]:
    """Copia todos los datos y devuelve cuántas filas se copiaron por tabla."""
    import_all_models()
    source = make_engine(normalize_database_url(source_url))
    target = make_engine(normalize_database_url(target_url))
    if target.dialect.name != "postgresql":
        raise ValueError("El destino debe ser PostgreSQL")

    run_migrations(target)
    tables = [t for t in Base.metadata.sorted_tables if t.name not in SKIP_TABLES]

    with target.connect() as conn:
        not_empty = [t.name for t in tables if t.name not in CATALOG_TABLES
                     and conn.execute(select(func.count()).select_from(t)).scalar_one()]
    if not_empty:
        raise ValueError(f"El destino no está vacío: {', '.join(not_empty)}")

    source_inspector = inspect(source)
    source_tables = set(source_inspector.get_table_names())
    counts: dict[str, int] = {}
    id_maps: dict[str, dict[str, str]] = {}
    with source.connect() as src, target.begin() as dst:
        for table in tables:
            if table.name not in source_tables:
                counts[table.name] = 0
                continue
            # Una base anterior puede no tener columnas nuevas: toman su valor por defecto
            source_columns = {c["name"] for c in source_inspector.get_columns(table.name)}
            columns = [c for c in table.columns if c.name in source_columns]
            result = src.execution_options(stream_results=True).execute(select(*columns))
            copied = 0
            while batch := result.mappings().fetchmany(BATCH_SIZE):
                rows = [dict(row) for row in batch]
                if table.name in CATALOG_TABLES:
                    rows = _merge_catalog(dst, table, CATALOG_TABLES[table.name], rows, id_maps)
                for column, catalog in CATALOG_REFERENCES.get(table.name, {}).items():
                    for row in rows:
                        row[column] = id_maps.get(catalog, {}).get(row[column], row[column])
                if rows:
                    dst.execute(table.insert(), rows)
                copied += len(rows)
            counts[table.name] = copied
            logger.info("%s: %d filas", table.name, copied)

    if reindex:
        counts["ems_chunk_embeddings"] = reindex_embeddings(target)
    return counts


def _merge_catalog(dst, table, key: str, rows: list[dict], id_maps: dict) -> list[dict]:
    """Devuelve solo las filas nuevas y registra qué id del destino corresponde a cada fila."""
    existing = dict(dst.execute(select(table.c[key], table.c.id)).all())
    mapping = id_maps.setdefault(table.name, {})
    new_rows = []
    for row in rows:
        if row[key] in existing:
            mapping[row["id"]] = existing[row[key]]
        else:
            new_rows.append(row)
    return new_rows


def reindex_embeddings(engine) -> int:
    """Calcula en pgvector el embedding de cada chunk de documentos procesados."""
    from app.ems.models import EMSChunk, EMSDocument
    from app.ems.providers import VectorRecord
    from app.ems.store import embedding_provider, get_vector_store

    total = 0
    with Session(engine) as db:
        store = get_vector_store(db)
        rows = (
            db.query(EMSChunk, EMSDocument)
            .join(EMSDocument, EMSChunk.document_id == EMSDocument.id)
            .filter(EMSDocument.status == "processed")
            .order_by(EMSChunk.id)
            .all()
        )
        for start in range(0, len(rows), 64):
            batch = rows[start:start + 64]
            vectors = embedding_provider.embed([chunk.content for chunk, _ in batch])
            store.upsert([
                VectorRecord(id=chunk.id, vector=vector, text=chunk.content,
                             metadata={"document_id": doc.id, "company_id": chunk.company_id})
                for (chunk, doc), vector in zip(batch, vectors)
            ])
            total += len(batch)
        db.commit()
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Migra los datos de ADÁN de SQLite a PostgreSQL")
    parser.add_argument("--from", dest="source", required=True, help="URL de SQLite de origen")
    parser.add_argument("--to", dest="target", required=True, help="URL de PostgreSQL de destino")
    parser.add_argument("--no-reindex", action="store_true", help="No recalcular embeddings")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    counts = migrate(args.source, args.target, reindex=not args.no_reindex)
    for name, count in counts.items():
        print(f"{name:28} {count:>8}")
    print(f"{'TOTAL':28} {sum(counts.values()):>8}")


if __name__ == "__main__":
    main()
