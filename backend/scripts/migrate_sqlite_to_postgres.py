"""Copia todos los datos de una base SQLite de ADÁN a PostgreSQL (WO-091).

Uso (desde backend/):
    python -m scripts.migrate_sqlite_to_postgres \
        --source sqlite:///data/adan.db \
        --target postgresql+psycopg://adan:adan@localhost:5432/adan

- Aplica las migraciones en ambos extremos (la BD SQLite antigua se adopta
  sin perder datos) y copia tabla por tabla respetando las FKs.
- Se niega a escribir en un destino que ya tenga datos, salvo `--force`
  (que vacía primero las tablas del destino).
"""
from __future__ import annotations

import argparse
import sys

from sqlalchemy import func, insert, select, text

from app.core.database import Base, create_db_engine, import_all_models
from app.core.migrations import upgrade_database

BATCH_SIZE = 500


def migrate(source_url: str, target_url: str, force: bool = False) -> dict[str, int]:
    import_all_models()
    source = create_db_engine(source_url)
    target = create_db_engine(target_url)
    upgrade_database(source)
    upgrade_database(target)

    tables = Base.metadata.sorted_tables
    with target.connect() as conn:
        non_empty = [t.name for t in tables if conn.execute(select(func.count()).select_from(t)).scalar()]
    if non_empty and not force:
        raise SystemExit(
            f"El destino ya tiene datos en: {', '.join(non_empty)}. Usa --force para reemplazarlos."
        )

    copied: dict[str, int] = {}
    with source.connect() as src, target.begin() as dst:
        if non_empty:
            names = ", ".join(f'"{t.name}"' for t in tables)
            dst.execute(text(f"TRUNCATE {names} CASCADE"))
        for table in tables:
            total = 0
            result = src.execution_options(stream_results=True).execute(select(table))
            while batch := result.fetchmany(BATCH_SIZE):
                dst.execute(insert(table), [dict(row._mapping) for row in batch])
                total += len(batch)
            copied[table.name] = total

    source.dispose()
    target.dispose()
    return copied


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, help="URL SQLite de origen")
    parser.add_argument("--target", required=True, help="URL PostgreSQL de destino")
    parser.add_argument("--force", action="store_true", help="vaciar el destino si tiene datos")
    args = parser.parse_args(argv)

    copied = migrate(args.source, args.target, args.force)
    for name, count in copied.items():
        if count:
            print(f"{name:28s} {count:>8d}")
    print(f"Total filas copiadas: {sum(copied.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
