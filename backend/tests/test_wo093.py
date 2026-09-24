"""WO-093 — Producción: observabilidad, readiness, límites en Redis, sandbox y dependencias.

Las pruebas de Redis corren con REDIS_TEST_URL (p. ej. redis://127.0.0.1:6390/15).
"""
import importlib.util
import logging
import os
import pathlib
import threading
from http.server import ThreadingHTTPServer

import pytest
from alembic import command
from prometheus_client import REGISTRY

from app.ai.base import LLMAdapter, LLMResponse
from app.ai.factory import InstrumentedLLM
from app.core import config as config_module
from app.core.auth import hash_password, verify_password
from app.core.config import production_problems, settings
from app.core.logging import JSONFormatter
from app.core.migrations import alembic_config
from app.core.observability import request_id_var
from app.core.ratelimit import RedisSlidingWindowLimiter
from app.main import app
from app.tef.executor import ToolExecutor
from app.tef.interfaces import ToolContext
from app.tef.registry import ToolRegistry
from app.tef.tools import PythonSandboxTool

REDIS_URL = os.getenv("REDIS_TEST_URL", "")
requires_redis = pytest.mark.skipif(not REDIS_URL, reason="requiere REDIS_TEST_URL")
PASSWORD = "clave-segura-2026"


def _sample(name, labels):
    return REGISTRY.get_sample_value(name, labels) or 0.0


# ============================================================
# Logs, métricas y trazas por correlación
# ============================================================

def test_every_response_has_a_request_id(client):
    generated = client.get("/health").headers["X-Request-ID"]
    assert len(generated) == 32
    assert client.get("/health", headers={"X-Request-ID": "trace-abc-123"}).headers["X-Request-ID"] == "trace-abc-123"
    # Un identificador inválido no se refleja: se genera otro
    assert client.get("/health", headers={"X-Request-ID": "<script>"}).headers["X-Request-ID"] != "<script>"


def test_log_lines_carry_the_request_id():
    token = request_id_var.set("req-42")
    try:
        record = logging.LogRecord("adan", logging.INFO, __file__, 1, "hola", None, None)
        assert '"request_id": "req-42"' in JSONFormatter().format(record)
    finally:
        request_id_var.reset(token)


def test_unhandled_errors_return_the_request_id(client):
    def boom():
        raise RuntimeError("falla inesperada")

    app.router.add_api_route("/__boom", boom)
    try:
        resp = client.get("/__boom", headers={"X-Request-ID": "req-500"})
    finally:
        app.router.routes.pop()
    assert resp.status_code == 500
    assert resp.json() == {"detail": "Error interno", "request_id": "req-500"}


def test_metrics_use_route_templates(client):
    headers = {"Authorization": "Bearer " + client.post("/api/v1/auth/register", json={
        "email": "m@example.com", "name": "M", "password": PASSWORD}).json()["access_token"]}
    labels = {"method": "GET", "route": "/api/v1/companies/{company_id}", "status": "404"}
    before = _sample("adan_http_requests_total", labels)
    client.get("/api/v1/companies/no-existe", headers=headers)
    assert _sample("adan_http_requests_total", labels) == before + 1
    body = client.get("/metrics").text
    assert "adan_http_request_duration_seconds_bucket" in body
    assert "no-existe" not in body  # la URL concreta no crea series


def test_metrics_can_require_a_token(client, monkeypatch):
    monkeypatch.setattr(settings, "METRICS_TOKEN", "t" * 40)
    assert client.get("/metrics").status_code == 401
    assert client.get("/metrics", headers={"Authorization": "Bearer " + "t" * 40}).status_code == 200


@pytest.mark.asyncio
async def test_llm_calls_are_measured():
    class Inner(LLMAdapter):
        async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
            return LLMResponse(content="ok", model="fake")

        async def generate(self, prompt, model=None, system=None, temperature=0.7, max_tokens=2048):
            raise RuntimeError("caído")

        async def health_check(self):
            return True

        def list_models(self):
            return []

    llm = InstrumentedLLM(Inner())
    ok_before = _sample("adan_llm_call_duration_seconds_count", {"operation": "chat", "outcome": "ok"})
    err_before = _sample("adan_llm_call_duration_seconds_count", {"operation": "generate", "outcome": "error"})
    await llm.chat([])
    with pytest.raises(RuntimeError):
        await llm.generate("x")
    assert _sample("adan_llm_call_duration_seconds_count", {"operation": "chat", "outcome": "ok"}) == ok_before + 1
    assert _sample("adan_llm_call_duration_seconds_count", {"operation": "generate", "outcome": "error"}) == err_before + 1


# ============================================================
# Healthchecks
# ============================================================

def test_readiness_requires_migrations_at_head(client, db_session):
    resp = client.get("/health/ready")
    assert resp.status_code == 503  # la base de pruebas se crea sin Alembic
    assert resp.json()["checks"]["database"] == "ok"
    assert "pendientes" in resp.json()["checks"]["migrations"]

    connection = db_session.connection()
    command.stamp(alembic_config(connection), "head")
    db_session.commit()
    try:
        resp = client.get("/health/ready")
        assert resp.status_code == 200, resp.json()
        assert resp.json()["checks"]["llm"].startswith(("ok", "degradado"))  # sin LLM sigue listo
    finally:
        db_session.execute(__import__("sqlalchemy").text("DROP TABLE alembic_version"))
        db_session.commit()


# ============================================================
# Límites compartidos en Redis
# ============================================================

@requires_redis
def test_redis_limits_are_shared_between_replicas():
    replica_a, replica_b = RedisSlidingWindowLimiter(REDIS_URL), RedisSlidingWindowLimiter(REDIS_URL)
    replica_a.reset()
    assert replica_a.hit("k", 3, 60) is None
    assert replica_b.hit("k", 3, 60) is None
    assert replica_a.hit("k", 3, 60) is None
    wait = replica_b.hit("k", 3, 60)  # la cuarta, desde otra réplica, ya no pasa
    assert wait is not None and 1 <= wait <= 61
    assert replica_a.blocked_for("k", 3, 60) is not None
    replica_b.reset("k")
    assert replica_a.hit("k", 3, 60) is None
    assert replica_a.ping()


@requires_redis
def test_redis_window_slides():
    limiter = RedisSlidingWindowLimiter(REDIS_URL)
    limiter.reset("w")
    assert limiter.hit("w", 1, 1) is None
    assert limiter.hit("w", 1, 1) is not None
    import time
    time.sleep(1.2)
    assert limiter.hit("w", 1, 1) is None


def test_redis_down_fails_open():
    limiter = RedisSlidingWindowLimiter("redis://127.0.0.1:1/0")
    assert limiter.hit("x", 1, 60) is None
    assert limiter.hit("x", 1, 60) is None
    assert limiter.ping() is False


# ============================================================
# Sandbox aislado
# ============================================================

@pytest.fixture
def sandbox_server(monkeypatch):
    path = pathlib.Path(__file__).resolve().parents[2] / "sandbox" / "sandbox.py"
    spec = importlib.util.spec_from_file_location("adan_sandbox", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.TOKEN = "s" * 40
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), module.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    monkeypatch.setattr(settings, "SANDBOX_URL", f"http://127.0.0.1:{httpd.server_address[1]}")
    monkeypatch.setattr(settings, "SANDBOX_TOKEN", "s" * 40)
    yield
    httpd.shutdown()


@pytest.mark.asyncio
async def test_python_runs_in_the_sandbox(sandbox_server):
    registry = ToolRegistry()
    registry.register(PythonSandboxTool())
    context = ToolContext(company_id="c", user_id="u", trace_id="t")
    result = await ToolExecutor(registry).execute("python_sandbox", {"code": "print(2 + 2)"}, context)
    assert result.status == "success" and result.output["stdout"] == "4\n"
    failed = await ToolExecutor(registry).execute("python_sandbox", {"code": "1/0"}, context)
    assert failed.status == "error" and "ZeroDivisionError" in failed.error


@pytest.mark.asyncio
async def test_without_sandbox_code_never_runs(monkeypatch):
    monkeypatch.setattr(settings, "SANDBOX_URL", "")
    registry = ToolRegistry()
    registry.register(PythonSandboxTool())
    context = ToolContext(company_id="c", user_id="u", trace_id="t")
    result = await ToolExecutor(registry).execute("python_sandbox", {"code": "print(1)"}, context)
    assert result.status == "permission_denied" and "execute:code" in result.error


def test_production_requires_a_strong_sandbox_token(monkeypatch):
    cfg = config_module.Settings()
    monkeypatch.setattr(cfg, "SANDBOX_URL", "http://sandbox:8100")
    monkeypatch.setattr(cfg, "SANDBOX_TOKEN", "corto")
    assert any("SANDBOX_TOKEN" in p for p in production_problems(cfg))


# ============================================================
# Dependencias: bcrypt directo (sin passlib) y PyJWT (sin python-jose)
# ============================================================

def test_passwords_hashed_by_passlib_still_work():
    legacy = "$2b$12$Si/Pjk0QoW0jx1EDyGCNqOem4CeD5Crp2F0e/9hED06UC9i1wp.RO"  # passlib 1.7.4
    assert verify_password("clave-vieja-2025", legacy)
    assert not verify_password("otra-clave-2025", legacy)
    assert not verify_password("x" * 80, legacy)  # más de 72 bytes: nunca válida
    assert verify_password(PASSWORD, hash_password(PASSWORD))
