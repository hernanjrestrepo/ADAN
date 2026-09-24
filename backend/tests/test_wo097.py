"""WO-097 — Seguridad y aislamiento por empresa."""
import asyncio

import pytest

from app.core import config as config_module
from app.core.auth import CSRF_HEADER, CSRF_VALUE, SESSION_COOKIE
from app.core.config import check_settings, production_problems, settings
from app.core.crypto import decrypt_json, encrypt_json
from app.core.net import BlockedURLError, ensure_public_url, host_is_allowed
from app.integrations.models import IntegrationConnection
from app.tef.executor import ToolExecutor
from app.tef.interfaces import ToolContext, ToolMetadata, ToolProvider, ToolResult
from app.tef.models import ToolAuditEntry
from app.tef.registry import ToolRegistry
from app.tef.tools import CalculatorTool, EmailSenderTool, FileReaderTool

PASSWORD = "clave-segura-2026"


def _register(client, email):
    resp = client.post("/api/v1/auth/register", json={"email": email, "name": "U", "password": PASSWORD})
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _company(client, headers, name="Acme"):
    return client.post("/api/v1/companies/", json={"name": name}, headers=headers).json()["id"]


@pytest.fixture
def tenants(client):
    """Dos usuarios, cada uno con su empresa. Las cookies del cliente se limpian."""
    a = _register(client, "a@example.com")
    b = _register(client, "b@example.com")
    client.cookies.clear()
    return {"a": a, "b": b, "company_a": _company(client, a, "A"), "company_b": _company(client, b, "B")}


# ============================================================
# S12 — secretos y configuración
# ============================================================

def test_there_is_no_public_default_jwt_secret():
    assert settings.JWT_SECRET != "adan-dev-secret-change-in-production"
    assert len(settings.JWT_SECRET) >= 32


def test_production_refuses_insecure_settings(monkeypatch):
    cfg = config_module.Settings()
    monkeypatch.setattr(cfg, "ADAN_ENV", "production")
    monkeypatch.setattr(cfg, "JWT_SECRET_IS_EPHEMERAL", True)
    monkeypatch.setattr(cfg, "ENCRYPTION_KEY", "")
    monkeypatch.setattr(cfg, "DATABASE_URL", "sqlite:///x.db")
    problems = production_problems(cfg)
    assert len(problems) == 3
    with pytest.raises(RuntimeError, match="producción"):
        check_settings(cfg)

    monkeypatch.setattr(cfg, "JWT_SECRET", "x" * 48)
    monkeypatch.setattr(cfg, "JWT_SECRET_IS_EPHEMERAL", False)
    monkeypatch.setattr(cfg, "ENCRYPTION_KEY", "k")
    monkeypatch.setattr(cfg, "DATABASE_URL", "postgresql+psycopg://adan:adan-dev@db/adan")
    assert production_problems(cfg) == ["La contraseña de PostgreSQL no puede ser la de desarrollo (POSTGRES_PASSWORD)"]
    monkeypatch.setattr(cfg, "DATABASE_URL", "postgresql+psycopg://adan:otra-clave@db/adan")
    check_settings(cfg)  # sin problemas, no falla


# ============================================================
# S14 — contraseñas, intentos y límites
# ============================================================

@pytest.mark.parametrize("password", ["corta1", "aaaaaaaaaaaa", "x" * 73, "nuevo@example.com", "nuevo-usuario"])
def test_weak_passwords_are_rejected(client, password):
    email = "nuevo-usuario@example.com" if password == "nuevo-usuario" else "nuevo@example.com"
    resp = client.post("/api/v1/auth/register", json={"email": email, "name": "U", "password": password})
    assert resp.status_code == 422


def test_login_is_locked_after_repeated_failures(client, monkeypatch):
    monkeypatch.setattr(settings, "LOGIN_MAX_FAILURES", 3)
    _register(client, "victima@example.com")
    for _ in range(3):
        assert client.post("/api/v1/auth/login", json={"email": "victima@example.com", "password": "mala-clave-123"}).status_code == 401
    locked = client.post("/api/v1/auth/login", json={"email": "victima@example.com", "password": PASSWORD})
    assert locked.status_code == 429 and "Retry-After" in locked.headers
    # Otra cuenta desde la misma IP no queda bloqueada
    _register(client, "otra@example.com")
    assert client.post("/api/v1/auth/login", json={"email": "otra@example.com", "password": PASSWORD}).status_code == 200


def test_registrations_per_ip_are_limited(client, monkeypatch):
    monkeypatch.setattr(settings, "REGISTER_PER_IP_PER_HOUR", 2)
    _register(client, "uno@example.com")
    _register(client, "dos@example.com")
    resp = client.post("/api/v1/auth/register", json={"email": "tres@example.com", "name": "U", "password": PASSWORD})
    assert resp.status_code == 429


def test_requests_per_ip_are_limited(client, monkeypatch):
    monkeypatch.setattr(settings, "RATE_LIMIT_PER_MINUTE", 3)
    codes = [client.get("/health").status_code for _ in range(4)]
    assert codes == [200, 200, 200, 429]


def test_llm_endpoints_have_a_per_user_limit(client, tenants, monkeypatch):
    monkeypatch.setattr(settings, "LLM_RATE_LIMIT_PER_MINUTE", 1)
    url = f"/api/v1/nivel1/{tenants['company_a']}/recommendations"
    first = client.post(url, headers=tenants["a"])
    assert first.status_code != 429  # 400: aún no hay diagnóstico
    assert client.post(url, headers=tenants["a"]).status_code == 429
    # El límite es por usuario
    assert client.post(f"/api/v1/nivel1/{tenants['company_b']}/recommendations", headers=tenants["b"]).status_code != 429


def test_oversized_bodies_and_messages_are_rejected(client, tenants, monkeypatch):
    long_message = "x" * 9000
    resp = client.post(f"/api/v1/nivel1/{tenants['company_a']}/chat", json={"message": long_message},
                       headers=tenants["a"])
    assert resp.status_code == 422
    monkeypatch.setattr(settings, "MAX_BODY_BYTES", 100)
    resp = client.post("/ems/ingest", json={"company_id": tenants["company_a"], "title": "t", "text": "y" * 500},
                       headers=tenants["a"])
    assert resp.status_code == 413


def test_security_headers(client):
    headers = client.get("/health").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"


# ============================================================
# S15 — sesión en cookie httpOnly, CSRF y revocación
# ============================================================

def test_session_cookie_is_httponly_and_works(client):
    resp = client.post("/api/v1/auth/register", json={"email": "c@example.com", "name": "C", "password": PASSWORD})
    cookie = resp.headers["set-cookie"]
    assert cookie.startswith(f"{SESSION_COOKIE}=") and "HttpOnly" in cookie and "samesite=lax" in cookie.lower()
    assert client.get("/api/v1/auth/me").json()["email"] == "c@example.com"


def test_cookie_requests_that_change_data_need_the_csrf_header(client):
    client.post("/api/v1/auth/register", json={"email": "d@example.com", "name": "D", "password": PASSWORD})
    blocked = client.post("/api/v1/companies/", json={"name": "Sin cabecera"})
    assert blocked.status_code == 403
    allowed = client.post("/api/v1/companies/", json={"name": "Con cabecera"}, headers={CSRF_HEADER: CSRF_VALUE})
    assert allowed.status_code == 201


def test_logout_revokes_every_token(client):
    headers = _register(client, "e@example.com")
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200
    resp = client.post("/api/v1/auth/logout", headers=headers)
    assert resp.status_code == 204
    assert f'{SESSION_COOKIE}=""' in resp.headers["set-cookie"] or "Max-Age=0" in resp.headers["set-cookie"]
    revoked = client.get("/api/v1/auth/me", headers=headers)
    assert revoked.status_code == 401 and revoked.json()["detail"] == "La sesión fue cerrada"
    # Un nuevo login emite un token válido
    token = client.post("/api/v1/auth/login", json={"email": "e@example.com", "password": PASSWORD}).json()["access_token"]
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200


# ============================================================
# Autorización centralizada
# ============================================================

@pytest.mark.parametrize("method,path", [
    ("get", "/ems/stats/{other}"),
    ("get", "/ems/documents/{other}"),
    ("get", "/api/v1/companies/{other}"),
    ("get", "/api/v1/companies/{other}/project"),
    ("get", "/api/v1/nivel1/{other}/decisions"),
    ("get", "/tef/audit/{other}"),
    ("get", "/integrations/connections/{other}"),
])
def test_other_companies_are_invisible(client, tenants, method, path):
    resp = getattr(client, method)(path.format(other=tenants["company_b"]), headers=tenants["a"])
    assert resp.status_code == 404


# ============================================================
# S13 — integraciones por empresa, con credenciales cifradas
# ============================================================

def test_connector_credentials_are_per_company_and_encrypted(client, db_session, tenants):
    secret = "api-key-super-secreta"
    resp = client.post("/integrations/connect", json={
        "company_id": tenants["company_a"], "connector_id": "rest_api",
        "credentials": {"base_url": "https://api.example.com", "api_key": secret},
    }, headers=tenants["a"])
    assert resp.json()["connected"] is True

    row = db_session.query(IntegrationConnection).one()
    assert secret not in row.credentials_encrypted
    assert decrypt_json(row.credentials_encrypted)["api_key"] == secret

    listed = client.get(f"/integrations/connections/{tenants['company_a']}", headers=tenants["a"]).json()
    assert listed == [{"connector_id": "rest_api", "status": "connected", "updated_at": listed[0]["updated_at"]}]

    # A usa sus credenciales; B no ve nada de A
    health_a = client.get(f"/integrations/health/{tenants['company_a']}/rest_api", headers=tenants["a"]).json()
    health_b = client.get(f"/integrations/health/{tenants['company_b']}/rest_api", headers=tenants["b"]).json()
    assert health_a["base_url"] == "https://api.example.com"
    assert health_b["status"] == "disconnected" and health_b["base_url"] == ""
    stolen = client.post("/integrations/connect", json={"company_id": tenants["company_a"], "connector_id": "gmail"},
                         headers=tenants["b"])
    assert stolen.status_code == 404

    client.post("/integrations/disconnect", json={"company_id": tenants["company_a"], "connector_id": "rest_api"},
                headers=tenants["a"])
    db_session.refresh(row)
    assert row.status == "disconnected" and decrypt_json(row.credentials_encrypted) == {}


def test_tampered_credentials_are_detected():
    token = encrypt_json({"k": "v"})
    assert decrypt_json(token) == {"k": "v"}
    with pytest.raises(ValueError):
        decrypt_json(token[:-4] + "AAAA")


# ============================================================
# S16 — TEF: permisos, confirmación, timeout y auditoría persistente
# ============================================================

class SlowTool(ToolProvider):
    def metadata(self):
        return ToolMetadata(id="slow", name="Slow", description="duerme", category="test",
                            timeout_seconds=1, retries=0)

    async def execute(self, params, context):
        await asyncio.sleep(3)
        return ToolResult(tool_id="slow", status="success")


@pytest.fixture
def tef_context(tenants):
    return ToolContext(company_id=tenants["company_a"], user_id="u", trace_id="t")


@pytest.mark.asyncio
async def test_tools_need_their_permissions(db_session, tef_context):
    registry = ToolRegistry()
    registry.register(FileReaderTool())
    result = await ToolExecutor(registry, db_session).execute("file_reader", {"path": "/etc/passwd"}, tef_context)
    assert result.status == "permission_denied" and "read:files" in result.error
    assert db_session.query(ToolAuditEntry).filter_by(tool_id="file_reader", status="permission_denied").count() == 1


@pytest.mark.asyncio
async def test_slow_tools_time_out(db_session, tef_context):
    registry = ToolRegistry()
    registry.register(SlowTool())
    result = await ToolExecutor(registry, db_session).execute("slow", {}, tef_context)
    assert result.status == "timeout"
    assert db_session.query(ToolAuditEntry).filter_by(tool_id="slow", status="timeout").count() == 1


def test_tools_that_need_confirmation_preview_first(client, db_session, tenants):
    body = {"tool_id": "email_sender", "company_id": tenants["company_a"],
            "params": {"to": "x@example.com", "subject": "Hola", "body": "Prueba"}}
    preview = client.post("/tef/execute", json=body, headers=tenants["a"]).json()
    assert preview["status"] == "confirmation_required"
    sent = client.post("/tef/execute", json={**body, "confirm": True}, headers=tenants["a"]).json()
    assert sent["status"] == "success"

    audit = client.get(f"/tef/audit/{tenants['company_a']}", headers=tenants["a"]).json()
    assert [e["status"] for e in audit] == ["confirmation_required", "success"]
    assert db_session.query(ToolAuditEntry).count() == 2  # persistida, no en memoria


@pytest.mark.asyncio
async def test_calculator_still_works_without_extra_permissions(db_session, tef_context):
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(EmailSenderTool())
    result = await ToolExecutor(registry, db_session).execute("calculator", {"expression": "6*7"}, tef_context)
    assert result.status == "success" and result.output["result"] == 42


# ============================================================
# Salida controlada
# ============================================================

@pytest.mark.asyncio
async def test_outbound_allowlist(monkeypatch):
    monkeypatch.setattr(settings, "OUTBOUND_ALLOWED_HOSTS", ["example.com"])
    assert host_is_allowed("example.com") and host_is_allowed("api.example.com")
    assert not host_is_allowed("example.com.evil.net")
    with pytest.raises(BlockedURLError, match="OUTBOUND_ALLOWED_HOSTS"):
        await ensure_public_url("https://evil.net/datos")


# ============================================================
# B20 — un modelo que no responde no tumba el Board Room
# ============================================================

@pytest.mark.asyncio
async def test_board_room_survives_llm_timeouts():
    """Hallado en la prueba de estrés: con 5 Board Rooms a la vez, el timeout de Ollama daba 500."""
    import httpx

    from app.nivel1.board_room import BoardRoom

    class TimeoutLLM:
        async def chat(self, **kwargs):
            raise httpx.ReadTimeout("sin respuesta")

    consensus = await BoardRoom(TimeoutLLM()).run("Dolor de prueba")
    assert consensus.decision == "NO_CONSENSUS"
    assert {v.vote for v in consensus.votes} == {"ABSTAIN"}
    assert "ReadTimeout" in consensus.votes[0].justification
