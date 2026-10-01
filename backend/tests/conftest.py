"""Test configuration.

Motor de pruebas configurable (WO-091):
- por defecto SQLite en memoria (StaticPool), sin dependencias externas;
- `TEST_DATABASE_URL=postgresql+psycopg://...` corre toda la suite contra
  PostgreSQL + pgvector (el esquema se crea con las migraciones de Alembic).

Las tablas se vacían antes de cada test.
"""
import os

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite://")
# La app no debe tocar la base de desarrollo durante los tests
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event, text  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.database import Base, create_db_engine, get_db, import_all_models  # noqa: E402
from app.main import app  # noqa: E402

import_all_models()
IS_SQLITE = TEST_DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    # Single in-memory engine shared across all connections
    _test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(_test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=_test_engine)
else:
    from app.core.migrations import upgrade_database

    _test_engine = create_db_engine(TEST_DATABASE_URL)
    with _test_engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    upgrade_database(_test_engine)

_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


def _clean_all_tables() -> None:
    tables = list(reversed(Base.metadata.sorted_tables))
    with _test_engine.begin() as conn:
        if IS_SQLITE:
            for table in tables:
                conn.execute(table.delete())
        else:
            names = ", ".join(f'"{t.name}"' for t in tables)
            conn.execute(text(f"TRUNCATE {names} CASCADE"))


@pytest.fixture(scope="function")
def db_session():
    """Fresh session — tables are cleaned before each test."""
    _clean_all_tables()
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
