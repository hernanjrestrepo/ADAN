"""Test configuration — SQLite en memoria por defecto; PostgreSQL si se define TEST_DATABASE_URL.

    TEST_DATABASE_URL=postgresql://postgres@127.0.0.1:5433/adan_test pytest

Las tablas se limpian antes de cada prueba.
"""
import os

# La app no corre migraciones al arrancar en pruebas: el esquema lo crea este archivo
os.environ.setdefault("AUTO_MIGRATE", "false")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import normalize_database_url
from app.core.database import Base, get_db, import_all_models, make_engine
from app.main import app

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if TEST_DATABASE_URL:
    _test_engine = make_engine(normalize_database_url(TEST_DATABASE_URL))
else:
    # Single in-memory engine shared across all connections
    _test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(_test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

import_all_models()
if _test_engine.dialect.name == "postgresql":
    with _test_engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.drop_all(bind=_test_engine)
Base.metadata.create_all(bind=_test_engine)
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Fresh session — tables are cleaned before each test."""
    # Delete all data from all tables (preserve schema)
    with _test_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()

    session = _TestSession()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
