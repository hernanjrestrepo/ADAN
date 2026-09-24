"""Database setup — SQLAlchemy con SQLite (desarrollo y pruebas) o PostgreSQL + pgvector.

Una sola base declarativa (`Base`) para todo el sistema: núcleo, EMS y OOS (WO-091).
El esquema lo crean las migraciones de Alembic (`backend/migrations`).
"""
from __future__ import annotations

import importlib
import logging
from pathlib import Path

from sqlalchemy import JSON, Enum, String, create_engine, event
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# JSON en SQLite, JSONB en PostgreSQL (comparable e indexable)
JSONType = JSON().with_variant(JSONB(), "postgresql")


def ensure_sqlite_dir(url: str) -> None:
    """Crea la carpeta del archivo SQLite; con otros motores no toca el disco."""
    if url.startswith("sqlite:///"):
        Path(url.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)


def is_postgres(bind) -> bool:
    return bind is not None and bind.dialect.name == "postgresql"


def make_engine(url: str):
    """Engine con los ajustes de cada motor."""
    if url.startswith("sqlite"):
        ensure_sqlite_dir(url)
        new_engine = create_engine(url, connect_args={"check_same_thread": False}, echo=False)

        # WAL para lecturas concurrentes; claves foráneas activas
        @event.listens_for(new_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return new_engine
    # PostgreSQL: las fechas sin zona se guardan en UTC, como en SQLite
    return create_engine(url, pool_pre_ping=True, connect_args={"options": "-c timezone=utc"}, echo=False)


engine = make_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


@event.listens_for(Session, "before_flush")
def _fit_bounded_strings(session, flush_context, instances):
    """Recorta el texto que no cabe en su columna.

    SQLite ignora `String(n)`; PostgreSQL lo hace cumplir. Títulos y temas que genera el
    LLM (p. ej. las acciones del Board que el OOS convierte en Work Orders) pueden pasar
    del límite: se recortan con un aviso en el log en lugar de fallar con 500.
    """
    for obj in list(session.new) + list(session.dirty):
        for prop in sa_inspect(obj).mapper.column_attrs:
            column = prop.columns[0]
            length = getattr(column.type, "length", None)
            if not length or not isinstance(column.type, String) or isinstance(column.type, Enum):
                continue
            value = getattr(obj, prop.key, None)
            if isinstance(value, str) and len(value) > length:
                logger.warning("Texto recortado en %s.%s: %d → %d caracteres",
                               column.table.name, column.name, len(value), length)
                setattr(obj, prop.key, value[:length])


def get_db():
    """FastAPI dependency — yields a DB session, closes after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def import_all_models() -> None:
    """Registra todos los modelos en `Base.metadata` (Alembic y create_all los necesitan)."""
    for module in ("app.models.models", "app.ems.models", "app.oos.models",
                   "app.integrations.models", "app.tef.models"):
        importlib.import_module(module)


def init_db() -> None:
    """Deja el esquema al día: migraciones de Alembic, o create_all si AUTO_MIGRATE=false."""
    import_all_models()
    if settings.AUTO_MIGRATE:
        from app.core.migrations import run_migrations
        run_migrations(engine)
    else:
        Base.metadata.create_all(bind=engine)
