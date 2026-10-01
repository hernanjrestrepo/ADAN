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
# Muchos tests registran usuarios desde la misma IP; el rate limit se prueba aparte
os.environ.setdefault("AUTH_RATE_LIMIT_PER_MINUTE", "0")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event, text  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.database import Base, create_db_engine, get_db, import_all_models  # noqa: E402
from app.core.migrations import upgrade_database  # noqa: E402
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

else:
    _test_engine = create_db_engine(TEST_DATABASE_URL)
    with _test_engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))

# El esquema de pruebas se crea con las migraciones reales (no con create_all)
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


# ============================================================
# Servidor HTTP local (sustituye a httpbin.org: tests herméticos)
# ============================================================

_SAMPLE_HTML = """<!DOCTYPE html>
<html><head><title>Café Andino — Informe de mercado</title>
<style>body { color: #333 }</style><script>var tracking = true;</script></head>
<body><h1>Café Andino</h1>
""" + "\n".join(
    f"<p>Párrafo {i}: el mercado de café especial en Colombia crece por la demanda de "
    "hoteles boutique, cafeterías de especialidad y exportación a Europa. Los productores "
    "pequeños mejoran márgenes con trazabilidad, certificación orgánica y venta directa.</p>"
    for i in range(1, 9)
) + "\n</body></html>"


class _LocalHandler(__import__("http.server").server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path.startswith("/html"):
            body, ctype = _SAMPLE_HTML.encode(), "text/html; charset=utf-8"
        elif self.path.startswith("/get"):
            import json
            body, ctype = json.dumps({"url": self.path, "ok": True}).encode(), "application/json"
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.fixture(scope="session")
def local_http_server():
    """URL base de un servidor HTTP local con /html y /get."""
    import threading
    from http.server import ThreadingHTTPServer

    server = ThreadingHTTPServer(("127.0.0.1", 0), _LocalHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


@pytest.fixture
def local_site(local_http_server, monkeypatch):
    """Servidor local + permiso de red privada (la protección SSRF lo bloquearía)."""
    monkeypatch.setenv("ALLOW_PRIVATE_HTTP", "true")
    return local_http_server


# ============================================================
# Servidor ADÁN real (uvicorn) para tests de carga/concurrencia
# ============================================================

@pytest.fixture(scope="module")
def live_server(tmp_path_factory):
    """Levanta la app en un puerto libre con su propia BD de pruebas."""
    import socket
    import threading
    import time

    import uvicorn

    if IS_SQLITE:
        engine = create_db_engine(f"sqlite:///{tmp_path_factory.mktemp('live') / 'live.db'}")
        upgrade_database(engine)
    else:
        engine = _test_engine
        _clean_all_tables()
    LiveSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = LiveSession()
        try:
            yield db
        finally:
            db.close()

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    app.dependency_overrides[get_db] = override_get_db
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", lifespan="off"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 15
    while not server.started and time.time() < deadline:
        time.sleep(0.05)
    assert server.started, "el servidor de pruebas no arrancó"

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    thread.join(timeout=10)
    app.dependency_overrides.pop(get_db, None)
    if IS_SQLITE:
        engine.dispose()
