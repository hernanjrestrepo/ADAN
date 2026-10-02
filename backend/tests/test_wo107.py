"""WO-107 — Evidencia y Scoring: jerarquía de AD-CMP-05, los 8 Scores de AD-FUNC-07 y Gate por evidencia."""
import pytest

from app.models.models import Company, Document, Level, NivelStatus, Project, Score
from app.nivel1.board_room import BoardConsensus
from app.scoring import service as scoring
from app.twin.models import Evidence


def _register(client, email):
    resp = client.post("/api/v1/auth/register", json={"email": email, "name": "U", "password": "password123"})
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def co(client, db_session):
    headers = _register(client, "evidencia@example.com")
    cid = client.post("/api/v1/companies/", json={"name": "Café Andino"}, headers=headers).json()["id"]
    project = db_session.query(Project).filter_by(company_id=cid).one()
    return {"id": cid, "headers": headers, "project": project, "base": f"/api/v1/scoring/{cid}"}


def _add(client, co, **body):
    return client.post(f"{co['base']}/evidence", json={"dimension": "problem", **body}, headers=co["headers"])


def _strong_evidence(client, co):
    for n in range(3):
        assert _add(client, co, claim=f"Estudio de mercado {n}: 40 % de tiendas pierde café", kind="external",
                    source=f"https://example.org/estudio-{n}").status_code == 201
    for n in range(2):
        assert _add(client, co, claim=f"Entrevisté a la tienda {n} y confirma el problema",
                    kind="testimony").status_code == 201


def _diagnosis(db_session, co):
    db_session.add(Document(project_id=co["project"].id, title="Diagnóstico del Dolor", content="d",
                            doc_type="diagnosis", origin="generated_by_adan"))
    db_session.commit()


# ============================================================
# Evidencia: jerarquía de validez (AD-CMP-05 §1)
# ============================================================

def test_client_registers_external_data_and_testimony(client, co):
    ext = _add(client, co, claim="El DANE reporta 12.000 tiendas de café", kind="external",
               source="https://www.dane.gov.co")
    assert ext.status_code == 201, ext.text
    assert ext.json()["kind_label"] == "Dato verificable externamente"
    assert ext.json()["created_by"].startswith("user:")
    test = _add(client, co, claim="Mis clientes se quejan del café que se pierde", kind="testimony")
    assert test.status_code == 201
    listed = client.get(f"{co['base']}/evidence", headers=co["headers"]).json()
    assert {e["kind"] for e in listed} == {"external", "testimony"}


def test_external_data_needs_a_source_and_client_cannot_claim_inference(client, co):
    no_source = _add(client, co, claim="Un dato sin fuente que nadie puede revisar", kind="external")
    assert no_source.status_code == 422
    assert "fuente" in no_source.json()["detail"]
    assert _add(client, co, claim="Yo infiero que el mercado es grande", kind="inference").status_code == 422
    assert _add(client, co, claim="corto", kind="testimony").status_code == 422
    assert _add(client, co, claim="Dimensión que no existe en AD-FUNC-07", kind="testimony",
                dimension="vibes").status_code == 422


def test_board_room_enters_only_as_agent_inference(db_session, co):
    project = co["project"]
    item = scoring.record_board_inference(
        db_session, project, BoardConsensus(decision="PROCEED", score=90, confidence=95, summary="s", votes=[]))
    db_session.commit()
    assert item.kind == "inference" and item.created_by == "agent:Board Room"
    assert item.confidence_level == 40.0  # techo de una inferencia
    assert scoring.record_board_inference(
        db_session, project, BoardConsensus(decision="PIVOT", score=50, confidence=50, summary="s", votes=[])) is None


def test_archived_evidence_leaves_the_score_but_is_never_deleted(client, db_session, co):
    _strong_evidence(client, co)
    first = client.post(f"{co['base']}/scores/problem/calculate", headers=co["headers"]).json()["latest"]
    ev_id = client.get(f"{co['base']}/evidence", headers=co["headers"]).json()[0]["id"]
    resp = client.post(f"{co['base']}/evidence/{ev_id}/archive", json={"reason": "La fuente era vieja"},
                       headers=co["headers"])
    assert resp.status_code == 200 and resp.json()["status"] == "archived"
    second = client.post(f"{co['base']}/scores/problem/calculate", headers=co["headers"]).json()["latest"]
    assert second["value"] != first["value"]
    assert db_session.get(Evidence, ev_id) is not None
    # El Score anterior sigue citando la evidencia que usó (Patrón C)
    old = db_session.get(Score, first["id"])
    assert ev_id in old.evidence["evidence_ids"]


# ============================================================
# Los 8 Scores (AD-FUNC-07)
# ============================================================

def test_overview_lists_the_8_scores_with_their_availability(client, co):
    scores = client.get(f"{co['base']}/scores", headers=co["headers"]).json()
    assert [s["key"] for s in scores] == ["problem", "solution", "business", "product", "market", "execution",
                                          "responsible", "venture"]
    by_key = {s["key"]: s for s in scores}
    assert by_key["problem"]["available"] and by_key["responsible"]["available"]
    assert by_key["solution"]["unavailable_reason"] == "Se abre en el Nivel 2"
    assert by_key["venture"]["unavailable_reason"] == "Nace en el Nivel 6"
    blocked = client.post(f"{co['base']}/scores/venture/calculate", headers=co["headers"])
    assert blocked.status_code == 409


def test_each_calculation_is_a_new_score_with_its_evidence(client, db_session, co):
    _strong_evidence(client, co)
    one = client.post(f"{co['base']}/scores/problem/calculate", headers=co["headers"]).json()
    client.post(f"{co['base']}/scores/problem/calculate", headers=co["headers"])
    rows = db_session.query(Score).filter_by(project_id=co["project"].id).all()
    assert len(rows) == 2  # nunca sobrescribe: serie histórica (AD-CMP-05 §4)
    assert one["latest"]["breakdown"]["external"]["supports"] == 3
    assert one["evidence_count"] == 5
    assert rows[0].evidence["engine"] == "AD-ARQ-10 v0"


def test_score_without_evidence_declares_zero_confidence(client, co):
    latest = client.post(f"{co['base']}/scores/problem/calculate", headers=co["headers"]).json()["latest"]
    assert latest["value"] == 0 and latest["confidence"] == 0
    assert "sin evidencia" in latest["reasoning"]


def test_responsible_score_is_about_the_person(client, db_session, co):
    latest = client.post(f"{co['base']}/scores/responsible/calculate", headers=co["headers"]).json()["latest"]
    assert latest["confidence"] == 0
    row = db_session.get(Score, latest["id"])
    assert row.subject == "responsible"
    assert row.user_id == db_session.get(Company, co["id"]).primary_user_id


def test_venture_score_opens_at_level_6(client, db_session, co):
    _strong_evidence(client, co)
    client.post(f"{co['base']}/scores/problem/calculate", headers=co["headers"])
    level6 = db_session.query(Level).filter_by(project_id=co["project"].id, number=6).one()
    level6.status = NivelStatus.ACTIVE
    db_session.commit()
    resp = client.post(f"{co['base']}/scores/venture/calculate", headers=co["headers"])
    assert resp.status_code == 200, resp.text
    assert resp.json()["latest"]["value"] > 0


# ============================================================
# Gate del Nivel 1 por evidencia (cierra B5)
# ============================================================

def test_gate_without_evidence_says_what_is_missing_and_proposes_nothing(client, db_session, co):
    _diagnosis(db_session, co)
    resp = client.post(f"/api/v1/nivel1/{co['id']}/gate-review", headers=co["headers"])
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["approved"] is False and body["decisions"] == []
    assert any("dato verificable" in m for m in body["missing"])
    assert "Todavía no hay evidencia suficiente" in body["message"]


def test_a_long_llm_diagnosis_no_longer_opens_the_gate(client, db_session, co):
    """B5: antes, un diagnóstico con las palabras clave aprobaba el Gate sin evidencia del cliente."""
    db_session.add(Document(project_id=co["project"].id, title="Diagnóstico del Dolor", doc_type="diagnosis",
                            origin="generated_by_adan",
                            content=("problema dolor necesidad solución mercado cliente competidor 500 empresas "
                                     "USD precio suscripción encuesta entrevista validación ") * 80))
    db_session.commit()
    assert client.post(f"/api/v1/nivel1/{co['id']}/gate-review", headers=co["headers"]).json()["approved"] is False


def test_gate_with_enough_evidence_proposes_closing_and_client_decides(client, db_session, co):
    _diagnosis(db_session, co)
    _strong_evidence(client, co)
    body = client.post(f"/api/v1/nivel1/{co['id']}/gate-review", headers=co["headers"]).json()
    assert body["approved"] is True and body["missing"] == []
    decision = body["decisions"][0]
    assert decision["recommended_option"] == "CLOSE"
    level1 = db_session.query(Level).filter_by(project_id=co["project"].id, number=1).one()
    assert level1.status == NivelStatus.ACTIVE  # nada se cierra sin el cliente
    resp = client.post(f"/api/v1/nivel1/{co['id']}/decisions/{decision['id']}", json={"action": "approve"},
                       headers=co["headers"])
    assert resp.status_code == 200, resp.text
    db_session.refresh(level1)
    assert level1.status == NivelStatus.COMPLETED


def test_advancing_without_evidence_is_the_clients_documented_responsibility(client, db_session, co):
    _diagnosis(db_session, co)
    resp = client.post(f"/api/v1/nivel1/{co['id']}/advance-anyway", headers=co["headers"])
    assert resp.status_code == 200, resp.text
    decision = resp.json()["decisions"][0]
    assert decision["recommended_option"] == "CONTINUE"
    close = next(o for o in decision["options"] if o["key"] == "CLOSE")
    assert close["evidence_level"] == "baja"

    url = f"/api/v1/nivel1/{co['id']}/decisions/{decision['id']}"
    bare = client.post(url, json={"action": "approve", "chosen_option": "CLOSE"}, headers=co["headers"])
    assert bare.status_code == 409  # decidir distinto exige riesgos y responsabilidad

    ok = client.post(url, json={"action": "approve", "chosen_option": "CLOSE",
                                "risks_assumed": ["Invertir sin validar el problema"],
                                "responsibility_statement": "Avanzo bajo mi responsabilidad: ya tengo clientes"},
                     headers=co["headers"])
    assert ok.status_code == 200, ok.text
    assert ok.json()["divergence"]["chosen_option"]["key"] == "CLOSE"
    level1 = db_session.query(Level).filter_by(project_id=co["project"].id, number=1).one()
    assert level1.status == NivelStatus.COMPLETED


def test_advance_anyway_is_refused_when_evidence_is_enough(client, db_session, co):
    _diagnosis(db_session, co)
    _strong_evidence(client, co)
    assert client.post(f"/api/v1/nivel1/{co['id']}/advance-anyway", headers=co["headers"]).status_code == 409


def test_gate_preview_does_not_store_scores(client, db_session, co):
    _add(client, co, claim="El DANE reporta 12.000 tiendas de café", kind="external", source="https://dane.gov.co")
    preview = client.get(f"{co['base']}/gate/1", headers=co["headers"]).json()
    assert preview["sufficient"] is False and preview["breakdown"]["external"]["supports"] == 1
    assert db_session.query(Score).filter_by(project_id=co["project"].id).count() == 0


def test_evidence_and_scores_are_private_to_their_company(client, co):
    _add(client, co, claim="Dato privado de la empresa con fuente", kind="external", source="https://x.org")
    other = _register(client, "otro@example.com")
    assert client.get(f"{co['base']}/evidence", headers=other).status_code == 404
    assert client.get(f"{co['base']}/scores", headers=other).status_code == 404
    assert _add(client, {**co, "headers": other}, claim="Intento escribir en otra empresa",
                kind="testimony").status_code == 404


def test_evidence_shows_up_in_the_timeline(client, co):
    _add(client, co, claim="El DANE reporta 12.000 tiendas de café", kind="external", source="https://dane.gov.co")
    client.post(f"{co['base']}/scores/problem/calculate", headers=co["headers"])
    events = client.get(f"/api/v1/twin/{co['id']}/timeline", headers=co["headers"]).json()
    types = [(e["event_type"], e["entity_type"]) for e in events]
    assert ("entity_created", "evidence") in types
    assert ("score_calculated", "scores") in types
