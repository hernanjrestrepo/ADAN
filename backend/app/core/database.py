"""Database setup — SQLAlchemy con PostgreSQL + pgvector (producción) o SQLite (desarrollo).

WO-091: una única base declarativa (`Base`) para todos los módulos y esquema
gestionado por Alembic (ver `app/core/migrations.py`).
"""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


def is_sqlite_url(url: str) -> bool:
    return url.startswith("sqlite")


def create_db_engine(url: str) -> Engine:
    """Crea un engine con la configuración adecuada para cada motor."""
    if is_sqlite_url(url):
        # Ensure data directory exists for file-based SQLite
        db_file = url.replace("sqlite:///", "", 1)
        if url.startswith("sqlite:///") and db_file and db_file != ":memory:":
            Path(db_file).parent.mkdir(parents=True, exist_ok=True)

        eng = create_engine(url, connect_args={"check_same_thread": False}, echo=False)

        # SQLite WAL mode for concurrent reads
        @event.listens_for(eng, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return eng

    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        # Timestamps naive almacenados siempre en UTC
        connect_args={"options": "-c timezone=utc"},
        echo=False,
    )


engine = create_db_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def import_all_models() -> None:
    """Registra en `Base.metadata` las tablas de todos los módulos."""
    import app.models.models  # noqa: F401
    import app.ems.models  # noqa: F401
    import app.oos.models  # noqa: F401


def get_db():
    """FastAPI dependency — yields a DB session, closes after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Lleva el esquema a la última migración de Alembic."""
    from app.core.migrations import upgrade_database

    upgrade_database(engine)
