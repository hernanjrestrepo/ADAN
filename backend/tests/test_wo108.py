"""WO-108 — Onboarding (AD-FUNC-06), consentimiento (AD-DEC-0002 d.8), evidencia externa y Vista de Nivel."""
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from app.core.config import settings
from app.models.models import (
    Company, Consent, Decision, DecisionStatus, Document, Event, Message, Project, User,
)
from app.scoring import external
from app.twin.hooks import TwinRuleError

PASSWORD = "password123"


def _register(client, email, consent=True, share=False):
    body = {"email": email, "name": "Ana María", "password": PASSWORD, "share_aggregated": share}
    if consent:
        body["accept_data_policy"] = True
    return client.post("/api/v1/auth/register", json=body)


def _headers(resp):
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def user(client):
    return _headers(_register(client, "ana@example.com"))


def _start(client, headers, name="Café Andino"):
    resp = client.post("/api/v1/onboarding/start", json={"company_name": name, "stage": "idea"}, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ============================================================
# Consentimiento de datos (Ley 1581 de 2012)
# ============================================================

def test_no_account_without_explicit_consent(client, db_session):
    resp = _register(client, "sin@example.com", consent=False)
    assert resp.status_code == 422
    assert "política de tratamiento de datos" in resp.text
    assert db_session.query(User).filter_by(email="sin@example.com").count() == 0


def test_signup_records_both_consents_with_policy_version(client, db_session):
    _headers(_register(client, "con@example.com", share=True))
    user_id = db_session.query(User).filter_by(email="con@example.com").one().id
    rows = {c.purpose: c for c in db_session.query(Consent).filter_by(user_id=user_id)}
    assert rows["data_processing"].granted is True
    assert rows["aggregated_intelligence"].granted is True
    assert rows["data_processing"].policy_version == "2026-10"


def test_changing_consent_keeps_the_previous_record(client, db_session, user):
    resp = client.post("/api/v1/onboarding/consents", json={"purpose": "aggregated_intelligence", "granted": True},
                       headers=user)
    assert resp.status_code == 200 and resp.json()["aggregated_intelligence"]["granted"] is True
    rows = db_session.query(Consent).filter_by(purpose="aggregated_intelligence").all()
    assert sorted(r.granted for r in rows) == [False, True]  # la constancia anterior no se pierde


def test_withdrawing_data_processing_is_a_deletion_request(client, user):
    resp = client.post("/api/v1/onboarding/consents", json={"purpose": "data_processing", "granted": False},
                       headers=user)
    assert resp.status_code == 409 and "supresión" in resp.json()["detail"]


def test_consents_are_append_only(db_session, client, user):
    row = db_session.query(Consent).first()
    row.granted = not row.granted
    with pytest.raises(TwinRuleError):
        db_session.flush()
    db_session.rollback()


# ============================================================
# Onboarding: la primera pregunta real cuanto antes (AD-FUNC-06)
# ============================================================

def test_onboarding_reaches_the_first_real_question(client, db_session, user):
    me = client.get("/api/v1/onboarding/me", headers=user).json()
    assert me["next"] == {"step": "company", "company_id": None}
    assert me["identity"]["label"] == "Usuario"

    started = _start(client, user)
    assert "¿qué problema quieres resolver" in started["first_question"]
    assert "Ana" in started["first_question"] and "Café Andino" in started["first_question"]

    status = client.get(f"/api/v1/nivel1/{started['company_id']}/status", headers=user).json()
    assert status["messages"][0]["role"] == "assistant"
    event = db_session.query(Event).filter_by(event_type="onboarding_first_question").one()
    assert event.data["target_seconds"] == 30 and event.data["seconds_since_signup"] >= 0

    me = client.get("/api/v1/onboarding/me", headers=user).json()
    assert me["next"]["step"] == "first_answer"
    assert me["identity"]["label"] == "Responsable de Empresa"


def test_recovery_resumes_from_the_last_real_step(client, db_session, user, monkeypatch):
    started = _start(client, user)
    project = db_session.query(Project).filter_by(company_id=started["company_id"]).one()
    conv_id = db_session.query(Message).filter_by(role="assistant").one().conversation_id
    db_session.add(Message(conversation_id=conv_id, role="user", content="Las tiendas botan café"))
    db_session.commit()
    assert client.get("/api/v1/onboarding/me", headers=user).json()["next"] == {
        "step": "done", "company_id": project.company_id}


def test_first_question_is_never_repeated(client, db_session, user):
    from app.onboarding.service import seed_first_question
    started = _start(client, user)
    company = db_session.get(Company, started["company_id"])
    assert seed_first_question(db_session, db_session.get(User, company.primary_user_id), company) is None
    assert db_session.query(Message).filter_by(role="assistant").count() == 1


def test_creating_a_company_from_the_dashboard_also_asks_first(client, db_session, user):
    cid = client.post("/api/v1/companies/", json={"name": "Panadería"}, headers=user).json()["id"]
    messages = client.get(f"/api/v1/nivel1/{cid}/status", headers=user).json()["messages"]
    assert len(messages) == 1 and "Panadería" in messages[0]["content"]


def test_progressive_identity_follows_real_evidence(client, db_session, user):
    started = _start(client, user)
    cid = started["company_id"]
    project = db_session.query(Project).filter_by(company_id=cid).one()
    identity = lambda: client.get("/api/v1/onboarding/me", headers=user).json()["identity"]  # noqa: E731
    assert identity()["next"]["label"] == "Líder Activo"

    db_session.add(Document(project_id=project.id, title="Diagnóstico", content="d", doc_type="diagnosis",
                            origin="generated_by_adan"))
    db_session.commit()
    assert identity()["label"] == "Líder Activo"

    resp = client.post(f"/api/v1/twin/{cid}/entities/business_decisions",
                       json={"title": "Vender en tiendas especializadas"}, headers=user)
    assert resp.status_code == 201, resp.text
    assert identity()["label"] == "Cliente Activo"

    decision = Decision(project_id=project.id, title="Canal", status=DecisionStatus.PROPOSED,
                        proposed_by="Board Room")
    db_session.add(decision)
    db_session.commit()
    for status in (DecisionStatus.APPROVED, DecisionStatus.EXECUTED):
        from app.twin.actor import Actor, acting_as
        with acting_as(Actor.user(db_session.get(Company, cid).primary_user_id)):
            decision.status = status
            db_session.commit()
    decision.executed_at = datetime.now(timezone.utc) - timedelta(days=45)
    db_session.commit()
    final = identity()
    assert final["label"] == "Embajador" and final["next"] is None


# ============================================================
# Evidencia externa: fuentes verificadas y CSI
# ============================================================

def test_external_source_is_opened_and_verified(client, db_session, user, local_site):
    cid = _start(client, user)["company_id"]
    resp = client.post(f"/api/v1/scoring/{cid}/evidence", json={
        "claim": "Informe de mercado del café de especialidad", "kind": "external",
        "source": f"{local_site}/html"}, headers=user)
    assert resp.status_code == 201, resp.text
    verification = resp.json()["verification"]
    assert verification["status"] == "verified"
    assert verification["title"] == "Café Andino — Informe de mercado"


def test_unreachable_source_is_recorded_honestly(client, user, local_site):
    cid = _start(client, user)["company_id"]
    resp = client.post(f"/api/v1/scoring/{cid}/evidence", json={
        "claim": "Una fuente que ya no existe en la web", "kind": "external",
        "source": f"{local_site}/no-existe"}, headers=user)
    assert resp.status_code == 201
    assert resp.json()["verification"]["status"] == "unreachable"


def test_private_addresses_are_never_fetched(client, user):
    cid = _start(client, user)["company_id"]
    resp = client.post(f"/api/v1/scoring/{cid}/evidence", json={
        "claim": "Intento de que ADÁN lea una red interna", "kind": "external",
        "source": "http://169.254.169.254/latest/meta-data"}, headers=user)
    assert resp.json()["verification"]["status"] == "blocked"


def test_csi_not_connected_is_said_plainly(client, user, monkeypatch):
    monkeypatch.setattr(settings, "CSI_BASE_URL", "")
    cid = _start(client, user)["company_id"]
    assert client.get(f"/api/v1/scoring/{cid}/csi", headers=user).json() == {"connected": False}
    resp = client.post(f"/api/v1/scoring/{cid}/csi/search", json={}, headers=user)
    assert resp.status_code == 503 and "CSI no está conectado" in resp.json()["detail"]


@pytest.fixture
def fake_csi(monkeypatch):
    """Servidor CSI simulado que habla el contrato v0 (POST /v0/signals)."""
    seen = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            seen.append({"path": self.path, "auth": self.headers.get("Authorization"), "body": body})
            payload = json.dumps({"signals": [
                {"claim": "El 38 % de las tiendas de café especial reporta merma semanal",
                 "source": "https://csi.example/estudios/merma-cafe", "polarity": "supports"},
                {"claim": "Sin fuente no cuenta", "source": "", "polarity": "supports"},
                {"claim": "Las ventas de café especial crecen 12 % anual en Colombia",
                 "source": "https://csi.example/indicadores/cafe", "polarity": "supports"},
            ]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setattr(settings, "CSI_BASE_URL", f"http://127.0.0.1:{server.server_address[1]}")
    monkeypatch.setattr(settings, "CSI_API_KEY", "clave-csi")

    async def fake_verify(url, timeout=6.0):
        return {"status": "verified", "title": "Fuente CSI", "checked_at": "2026-10-02T00:00:00+00:00"}

    monkeypatch.setattr(external, "verify_source", fake_verify)
    yield seen
    server.shutdown()


def test_csi_proposes_external_evidence_that_counts_only_when_confirmed(client, user, fake_csi):
    cid = _start(client, user)["company_id"]
    resp = client.post(f"/api/v1/scoring/{cid}/csi/search", json={"query": "merma de café"}, headers=user)
    assert resp.status_code == 200, resp.text
    proposed = resp.json()
    assert len(proposed) == 2  # la señal sin fuente se descarta
    assert all(p["confirmed"] is False and p["created_by"] == "agent:CSI" for p in proposed)
    assert fake_csi[0]["path"] == "/v0/signals" and fake_csi[0]["auth"] == "Bearer clave-csi"
    assert fake_csi[0]["body"]["purpose"] == "pain_validation"

    gate = client.get(f"/api/v1/scoring/{cid}/gate/1", headers=user).json()
    assert gate["breakdown"]["external"]["supports"] == 0  # propuesto no cuenta

    for item in proposed:
        assert client.post(f"/api/v1/scoring/{cid}/evidence/{item['id']}/confirm", headers=user).json()["confirmed"]
    gate = client.get(f"/api/v1/scoring/{cid}/gate/1", headers=user).json()
    assert gate["breakdown"]["external"]["supports"] == 2

    again = client.post(f"/api/v1/scoring/{cid}/csi/search", json={"query": "merma de café"}, headers=user).json()
    assert again == []  # no repite lo que ya está


# ============================================================
# Vista de Nivel y Cards
# ============================================================

def test_levels_view_shows_the_route_cards_and_scores(client, user):
    cid = _start(client, user)["company_id"]
    levels = client.get(f"/api/v1/companies/{cid}/levels", headers=user).json()
    assert [lv["number"] for lv in levels] == [1, 2, 3, 4, 5, 6, 7]
    first = levels[0]
    assert first["status"] == "active" and first["deliverable"] == "Diagnóstico del Dolor"
    assert first["cards"][0]["card_type"] == "pain_discovery"
    assert all(lv["status"] == "blocked" for lv in levels[1:])

    client.post(f"/api/v1/scoring/{cid}/evidence", json={"claim": "Tres tiendas confirman la merma",
                                                         "kind": "testimony"}, headers=user)
    client.post(f"/api/v1/scoring/{cid}/scores/problem/calculate", headers=user)
    first = client.get(f"/api/v1/companies/{cid}/levels", headers=user).json()[0]
    assert first["score"]["value"] > 0


def test_levels_are_private(client, user):
    cid = _start(client, user)["company_id"]
    other = _headers(_register(client, "otra@example.com"))
    assert client.get(f"/api/v1/companies/{cid}/levels", headers=other).status_code == 404
