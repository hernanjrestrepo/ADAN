"""WO-093 — Seguridad: aislamiento entre clientes y endurecimiento de la API."""
import pytest

from app.oos.services import OrganizationService, WorkOrderService


def _register(client, email: str) -> dict:
    resp = client.post("/api/v1/auth/register", json={
        "email": email, "name": email.split("@")[0], "password": "secret123",
    })
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def tenants(client, db_session):
    """Dos clientes; A tiene empresa, organización y una work order."""
    alice = _register(client, "alice@cliente-a.com")
    bob = _register(client, "bob@cliente-b.com")
    company = client.post("/api/v1/companies/", json={"name": "A Corp"}, headers=alice).json()
    org = OrganizationService(db_session).create(company["id"], "A Org")
    wo = WorkOrderService(db_session).create_from_decision(
        organization_id=org.id, decision_id=None, title="Secreta de A",
    )
    db_session.commit()
    return {"alice": alice, "bob": bob, "company": company, "org": org, "wo": wo}


class TestOOSIsolation:
    def test_owner_can_access(self, client, tenants):
        t = tenants
        resp = client.get(f"/oos/workorders/{t['org'].id}", headers=t["alice"])
        assert resp.status_code == 200
        assert [w["title"] for w in resp.json()] == ["Secreta de A"]

    @pytest.mark.parametrize("method,path", [
        ("get", "/oos/workorders/{org}"),
        ("get", "/oos/dashboard/{org}"),
        ("get", "/oos/kpis/{org}"),
        ("get", "/oos/risks/{org}"),
        ("patch", "/oos/workorders/{wo}"),
        ("post", "/oos/workorders/{wo}/start"),
        ("post", "/oos/workorders/{wo}/complete"),
    ])
    def test_other_tenant_gets_404(self, client, tenants, method, path):
        t = tenants
        url = path.format(org=t["org"].id, wo=t["wo"].id)
        kwargs = {"json": {"status": "cancelled"}} if method == "patch" else {}
        resp = getattr(client, method)(url, headers=t["bob"], **kwargs)
        assert resp.status_code == 404

    @pytest.mark.parametrize("path,body", [
        ("/oos/workorders", {"title": "Intrusa"}),
        ("/oos/kpis", {"name": "kpi", "category": "x", "target_value": 1}),
        ("/oos/risks", {"title": "riesgo", "description": "", "probability": 0.5, "impact": 0.5}),
        ("/oos/meetings", {"title": "reunión"}),
    ])
    def test_other_tenant_cannot_write(self, client, tenants, path, body):
        t = tenants
        resp = client.post(path, json={"organization_id": t["org"].id, **body}, headers=t["bob"])
        assert resp.status_code in (404, 422)
        assert resp.status_code == 404 or "organization_id" not in resp.text

    def test_work_order_untouched_after_attack(self, client, tenants, db_session):
        t = tenants
        client.post(f"/oos/workorders/{t['wo'].id}/complete", headers=t["bob"])
        db_session.refresh(t["wo"])
        assert t["wo"].status == "pending"


class TestIntegrationsIsolation:
    def test_connections_are_per_user(self, client, tenants):
        t = tenants
        resp = client.post("/integrations/connect", json={
            "connector_id": "gmail", "credentials": {"token": "secreto-de-alice"},
        }, headers=t["alice"])
        assert resp.json()["connected"] is True

        alice_health = client.get("/integrations/health/gmail", headers=t["alice"]).json()
        bob_health = client.get("/integrations/health/gmail", headers=t["bob"]).json()
        assert alice_health["status"] == "healthy"
        assert bob_health["status"] != "healthy"


# ============================================================
# Autenticación
# ============================================================

# Hash generado por la implementación anterior (passlib) para "secret123"
LEGACY_PASSLIB_HASH = "$2b$12$pSnrmYn6rIPBGFEq70JwLeTEZp.rqM1wxondBNk4o6d26bA6sdomG"


class TestAuthHardening:
    def test_legacy_passlib_hashes_still_verify(self):
        from app.core.auth import verify_password
        assert verify_password("secret123", LEGACY_PASSLIB_HASH)
        assert not verify_password("otra-clave", LEGACY_PASSLIB_HASH)
        assert not verify_password("secret123", "no-es-un-hash")

    def test_long_passwords_are_supported(self):
        from app.core.auth import hash_password, verify_password
        long_pw = "ñ" * 80  # 160 bytes > límite de 72 de bcrypt
        assert verify_password(long_pw, hash_password(long_pw))

    def test_tampered_or_expired_tokens_are_rejected(self, client):
        import jwt as pyjwt
        from datetime import datetime, timedelta, timezone
        from app.core.config import settings

        headers = _register(client, "token@test.com")
        token = headers["Authorization"].split()[1]
        assert client.get("/api/v1/auth/me", headers=headers).status_code == 200

        forged = pyjwt.encode({"sub": "x", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, "otro-secreto-de-un-atacante-con-32-bytes", algorithm="HS256")
        expired = pyjwt.encode({"sub": "x", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)}, settings.JWT_SECRET, algorithm="HS256")
        no_exp = pyjwt.encode({"sub": "x"}, settings.JWT_SECRET, algorithm="HS256")
        for bad in (forged, expired, no_exp, token[:-3] + "abc"):
            resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {bad}"})
            assert resp.status_code == 401, bad

    def test_inactive_user_cannot_login_or_use_token(self, client, db_session):
        from app.models.models import EntityStatus, User

        headers = _register(client, "baja@test.com")
        user = db_session.query(User).filter(User.email == "baja@test.com").one()
        user.status = EntityStatus.ARCHIVED
        db_session.commit()

        assert client.get("/api/v1/auth/me", headers=headers).status_code == 401
        resp = client.post("/api/v1/auth/login", json={"email": "baja@test.com", "password": "secret123"})
        assert resp.status_code == 401

    def test_login_is_rate_limited(self, client, monkeypatch):
        from app.core.config import settings
        from app.core.security import auth_rate_limiter

        monkeypatch.setattr(settings, "AUTH_RATE_LIMIT_PER_MINUTE", 3)
        auth_rate_limiter.reset()
        body = {"email": "nadie@test.com", "password": "incorrecta"}
        codes = [client.post("/api/v1/auth/login", json=body).status_code for _ in range(4)]
        assert codes == [401, 401, 401, 429]
        last = client.post("/api/v1/auth/login", json=body)
        assert int(last.headers["Retry-After"]) >= 1
        auth_rate_limiter.reset()


# ============================================================
# Cabeceras, errores, observabilidad
# ============================================================

class TestHTTPHardening:
    def test_security_headers(self, client):
        resp = client.get("/health")
        assert resp.headers["x-content-type-options"] == "nosniff"
        assert resp.headers["x-frame-options"] == "DENY"
        assert "default-src 'none'" in resp.headers["content-security-policy"]

    def test_request_id_is_generated_and_propagated(self, client):
        generated = client.get("/health").headers["x-request-id"]
        assert len(generated) == 32
        assert client.get("/health", headers={"X-Request-ID": "trace-abc.123"}).headers["x-request-id"] == "trace-abc.123"
        # valores inválidos no se reflejan (evita inyección en logs/cabeceras)
        assert client.get("/health", headers={"X-Request-ID": "a b<script>"}).headers["x-request-id"] != "a b<script>"

    def test_integrity_errors_return_409(self, client, tenants, db_session):
        # una work order con decision_id inexistente viola la FK → 409, no 500
        from app.oos.services import WorkOrderService
        from fastapi import Depends
        from app.core.database import get_db
        from app.main import app

        @app.get("/_test/integrity")
        def _boom(db=Depends(get_db)):
            WorkOrderService(db).create_from_decision(
                organization_id=tenants["org"].id, decision_id="no-existe", title="x",
            )
            db.commit()

        try:
            resp = client.get("/_test/integrity")
            assert resp.status_code == 409
            db_session.rollback()
        finally:
            app.router.routes = [r for r in app.router.routes if getattr(r, "path", "") != "/_test/integrity"]

    def test_unhandled_errors_return_500_with_request_id(self, client):
        from app.main import app

        @app.get("/_test/crash")
        def _crash():
            raise RuntimeError("detalle interno que no debe filtrarse")

        try:
            resp = client.get("/_test/crash", headers={"X-Request-ID": "req-500"})
            assert resp.status_code == 500
            assert resp.json() == {"detail": "Error interno", "request_id": "req-500"}
            assert "detalle interno" not in resp.text
        finally:
            app.router.routes = [r for r in app.router.routes if getattr(r, "path", "") != "/_test/crash"]

    def test_metrics_use_route_templates(self, client, tenants):
        client.get(f"/oos/workorders/{tenants['org'].id}", headers=tenants["alice"])
        body = client.get("/metrics").text
        assert "adan_http_requests_total" in body
        assert 'route="/oos/workorders/{organization_id}"' in body
        assert tenants["org"].id not in body

    def test_readiness(self, client):
        resp = client.get("/health/ready")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ready", "checks": {"database": "ok", "migrations": "ok"}}


class TestProductionConfig:
    @staticmethod
    def _settings(**overrides):
        from app.core.config import Settings
        cfg = Settings()
        for key, value in overrides.items():
            setattr(cfg, key, value)
        return cfg

    def test_development_has_no_blocking_errors(self):
        assert self._settings().validate() == []

    def test_production_rejects_insecure_defaults(self, monkeypatch):
        from app.core.config import DEFAULT_JWT_SECRET
        monkeypatch.delenv("ENABLE_DOCS", raising=False)
        cfg = self._settings(
            ENVIRONMENT="production", JWT_SECRET=DEFAULT_JWT_SECRET,
            DATABASE_URL="sqlite:///x.db", CORS_ORIGINS=["*"],
        )
        assert len(cfg.validate()) == 3
        assert cfg.docs_enabled is False

    def test_production_rejects_short_secret(self):
        cfg = self._settings(
            ENVIRONMENT="production", JWT_SECRET="corto",
            DATABASE_URL="postgresql+psycopg://u:p@db/adan", CORS_ORIGINS=["https://adan.example.com"],
        )
        assert cfg.validate() == ["JWT_SECRET debe definirse con al menos 32 caracteres aleatorios"]

    def test_production_accepts_secure_config(self):
        cfg = self._settings(
            ENVIRONMENT="production", JWT_SECRET="s" * 48,
            DATABASE_URL="postgresql+psycopg://u:p@db/adan", CORS_ORIGINS=["https://adan.example.com"],
        )
        assert cfg.validate() == []
