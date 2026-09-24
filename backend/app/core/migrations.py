"""Migraciones de Alembic al arrancar (WO-091)."""
from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine, inspect

logger = logging.getLogger(__name__)
# Alembic anuncia cada plugin al cargarse; no aporta al log de arranque
logging.getLogger("alembic.runtime.plugins").setLevel(logging.WARNING)

BACKEND_DIR = Path(__file__).resolve().parents[2]
INITIAL_REVISION = "0001"


def alembic_config(connection=None) -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    if connection is not None:
        cfg.attributes["connection"] = connection
    return cfg


def include_object_for(dialect_name: str):
    """Filtro de Alembic: ignora objetos que solo existen en otro motor (`ddl_if`)."""
    def include_object(obj, name, type_, reflected, compare_to):
        ddl_if = getattr(obj, "_ddl_if", None)
        return not (ddl_if is not None and ddl_if.dialect and ddl_if.dialect != dialect_name)
    return include_object


def _initial_schema() -> MetaData:
    """El esquema exacto de la migración inicial, reflejado desde una base SQLite temporal."""
    scratch = create_engine("sqlite://")
    with scratch.begin() as connection:
        command.upgrade(alembic_config(connection), INITIAL_REVISION)
    metadata = MetaData()
    metadata.reflect(bind=scratch)
    metadata.remove(metadata.tables["alembic_version"])
    scratch.dispose()
    return metadata


def run_migrations(engine) -> None:
    """Lleva la base a la última migración.

    Una base SQLite creada con `create_all` antes de WO-091 no tiene `alembic_version`:
    se completan las tablas de la migración inicial que le falten, se marca como
    `0001` y las migraciones siguientes hacen el resto. Los datos no se tocan.
    """
    with engine.begin() as connection:
        cfg = alembic_config(connection)
        tables = set(inspect(connection).get_table_names())
        if "alembic_version" not in tables and "users" in tables:
            if connection.dialect.name != "sqlite":
                raise RuntimeError("Base sin versión de Alembic: la adopción automática solo existe para SQLite")
            logger.warning("Base sin versión de Alembic: se adopta como %s", INITIAL_REVISION)
            _initial_schema().create_all(bind=connection, checkfirst=True)
            command.stamp(cfg, INITIAL_REVISION)
        command.upgrade(cfg, "head")
