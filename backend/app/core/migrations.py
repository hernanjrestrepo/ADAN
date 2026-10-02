"""Ejecución de migraciones Alembic desde la aplicación (WO-091)."""
from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
BASELINE_REVISION = "0001"
# Clave del advisory lock de PostgreSQL que serializa las migraciones cuando
# arrancan varios workers/réplicas a la vez.
_MIGRATION_LOCK_KEY = 0x41444E01


def alembic_config() -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["configure_logger"] = False
    return cfg


def upgrade_database(engine: Engine) -> None:
    """Aplica todas las migraciones pendientes.

    Una base creada antes de WO-091 (con `create_all`, sin tabla
    `alembic_version`) se marca primero en la revisión baseline para no
    intentar recrear tablas existentes; luego se aplican las posteriores.
    """
    cfg = alembic_config()
    with engine.begin() as connection:
        if connection.dialect.name == "postgresql":
            connection.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": _MIGRATION_LOCK_KEY})
        cfg.attributes["connection"] = connection
        tables = set(inspect(connection).get_table_names())
        if "alembic_version" not in tables and "users" in tables:
            logger.info("Base existente sin Alembic: stamp %s", BASELINE_REVISION)
            command.stamp(cfg, BASELINE_REVISION)
        command.upgrade(cfg, "head")
