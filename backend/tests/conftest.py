"""Test configuration — SQLite en memoria por defecto; PostgreSQL si se define TEST_DATABASE_URL.

    TEST_DATABASE_URL=postgresql://postgres@127.0.0.1:5433/adan_test pytest

Las tablas se limpian antes de cada prueba.
"""
import os

# La app no corre migraciones al arrancar en pruebas: el esquema lo crea este archivo
os.environ.setdefault("AUTO_MIGRATE", "false")
os.environ.setdefault("ADAN_ENV", "test")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import normalize_database_url
from app.core.database import Base, get_db, import_all_models, make_engine
from app.core.ratelimit import limiter
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


@pytest.fixture(autouse=True)
def _reset_rate_limits():
    """Cada prueba empieza sin intentos acumulados."""
    limiter.reset()
    yield


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


# ============================================================
# Red local para pruebas herméticas (WO-098 Sprint 0)
# ============================================================
# Antes, DKA e integraciones dependían de httpbin.org (servicio externo, inestable)
# y algunas aserciones pasaban en silencio si la red fallaba.

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


def _local_handler():
    import json
    from http.server import BaseHTTPRequestHandler

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if self.path.startswith("/html"):
                body, ctype = _SAMPLE_HTML.encode(), "text/html; charset=utf-8"
            elif self.path.startswith("/get"):
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

    return Handler


@pytest.fixture(scope="session")
def local_http_server():
    """URL base de un servidor HTTP local con /html y /get."""
    import threading
    from http.server import ThreadingHTTPServer

    server = ThreadingHTTPServer(("127.0.0.1", 0), _local_handler())
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


@pytest.fixture
def local_site(local_http_server, monkeypatch):
    """Servidor local accesible para las herramientas.

    La protección SSRF (app/core/net.py) bloquea con razón las direcciones no públicas;
    aquí se autoriza solo 127.0.0.1 y el resto sigue validándose igual.
    """
    from urllib.parse import urlparse

    import app.core.net as net

    original = net.ensure_public_url

    async def allow_loopback(url: str) -> None:
        if urlparse(url).hostname == "127.0.0.1":
            return
        await original(url)

    monkeypatch.setattr(net, "ensure_public_url", allow_loopback)
    return local_http_server


# ============================================================
# Servidor ADÁN real (uvicorn) para pruebas de concurrencia
# ============================================================

@pytest.fixture(scope="module")
def live_server(tmp_path_factory):
    """La app servida por uvicorn en un puerto libre, con su propia base y un LLM simulado.

    Si se define STRESS_BASE_URL, se usa ese servidor (p. ej. uno con Ollama real) en su lugar.
    """
    external = os.getenv("STRESS_BASE_URL")
    if external:
        yield external.rstrip("/")
        return

    import socket
    import threading
    import time

    import uvicorn

    import app.api.v1.nivel1 as nivel1_api
    from app.core.config import settings
    from tests.fakes import FakeLLM

    if _test_engine.dialect.name == "postgresql":
        engine = _test_engine
    else:
        engine = make_engine(f"sqlite:///{tmp_path_factory.mktemp('live') / 'live.db'}")
        Base.metadata.create_all(bind=engine)
    LiveSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = LiveSession()
        try:
            yield db
        finally:
            db.close()

    mp = pytest.MonkeyPatch()
    # Muchos registros desde una sola IP, como en una prueba de carga
    mp.setattr(settings, "REGISTER_PER_IP_PER_HOUR", 1000)
    mp.setattr(settings, "LLM_RATE_LIMIT_PER_MINUTE", 1000)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[nivel1_api.get_llm] = lambda: FakeLLM()

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
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
    app.dependency_overrides.clear()
    mp.undo()
    if engine is not _test_engine:
        engine.dispose()
