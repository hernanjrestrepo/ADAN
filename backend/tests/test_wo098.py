"""WO-098 — Gemelo Digital: entidades, Contrato Base, 4 Patrones, versionado y eventos."""
import pytest
from sqlalchemy import text

from app.models.models import (
    Company, Decision, DecisionStatus, Event, Level, NivelStatus, Project, Score, ScoreType,
)
from app.services.gemelo_digital import GemeloDigitalService
from app.twin.actor import Actor, acting_as
from app.twin.hooks import TwinRuleError
from app.twin.models import (
    Brand, BusinessOccurrence, CompanyInitiative, EntityVersion, LevelTask, TwinLineage,
)
from app.twin.registry import KINDS


def _register(client, email):
    resp = client.post("/api/v1/auth/register", json={"email": email, "name": "U", "password": "password123"})
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def twin(client, db_session):
    headers = _register(client, "gemelo@example.com")
    company_id = client.post("/api/v1/companies/", json={"name": "Café Andino"}, headers=headers).json()["id"]
    user_id = db_session.get(Company, company_id).primary_user_id
    return {"id": company_id, "headers": headers, "user_id": user_id,
            "base": f"/api/v1/twin/{company_id}"}


def _create(client, twin, kind, body):
    resp = client.post(f"{twin['base']}/entities/{kind}", json=body, headers=twin["headers"])
    assert resp.status_code == 201, resp.text
    return resp.json()


# ============================================================
# Catálogo: 38 entidades = 26 de negocio + 12 operativas
# ============================================================

def test_catalog_covers_the_23_missing_business_entities_and_risk(client, twin):
    kinds = client.get("/api/v1/twin/kinds", headers=twin["headers"]).json()
    assert len(kinds) == 24  # 23 entidades nuevas de AD-005 + Riesgo (transversal)
    labels = {k["label"] for k in kinds}
    assert {"Marca", "Cargo", "Rol Funcional", "Competidor", "Suceso Empresarial", "Decisión de Negocio",
            "Meta", "Indicador", "Activo", "Pasivo", "Ingreso", "Gasto", "Riesgo"} <= labels
    assert next(k for k in kinds if k["key"] == "initiatives")["pattern"] == "A"
    assert next(k for k in kinds if k["key"] == "business_occurrences")["pattern"] == "C"


def test_all_38_entities_of_ad006_exist():
    from app.core.database import Base
    business = {"companies", "founding_narratives", "documents"} | {k.model.__tablename__ for k in KINDS.values()
                                                                    if k.key != "risks"}
    operational = {"users", "projects", "workspaces", "levels", "cards", "conversations", "agents", "tasks",
                   "decisions", "scores", "events"}
    assert len(business) == 26
    # Usuario Principal es un rol de Usuario sobre la Empresa (companies.primary_user_id), no otra tabla
    assert len(operational) + 1 == 12
    assert business | operational <= set(Base.metadata.tables)


def test_agent_catalog_has_the_board_roles(client, twin):
    agents = client.get("/api/v1/twin/agents", headers=twin["headers"]).json()
    assert {a["code"] for a in agents} == {"ADAN", "CEO", "CTO", "CFO", "CMO", "Legal", "Producto", "Operaciones"}


# ============================================================
# Contrato Base: versión, responsable, historia y eventos
# ============================================================

def test_create_update_archive_restore_keeps_full_history(client, db_session, twin):
    brand = _create(client, twin, "brands", {"name": "Andino", "positioning": "Premium",
                                             "confidence_level": 80, "evidence_source": "Entrevista"})
    assert brand["version"] == 1
    assert brand["created_by"] == brand["updated_by"] == f"user:{twin['user_id']}"
    assert brand["evidence_source"] == "Entrevista"

    url = f"{twin['base']}/entities/brands/{brand['id']}"
    updated = client.patch(url, json={"positioning": "Café de origen", "reason": "Nuevo foco"},
                           headers=twin["headers"]).json()
    assert updated["version"] == 2 and updated["positioning"] == "Café de origen"

    assert client.post(f"{url}/archive", json={"reason": "Marca retirada"}, headers=twin["headers"]).json()["status"] == "archived"
    listed = client.get(f"{twin['base']}/entities/brands", headers=twin["headers"]).json()
    assert listed == []  # archivada: no aparece, pero no se borró
    assert len(client.get(f"{twin['base']}/entities/brands?include_archived=true", headers=twin["headers"]).json()) == 1
    assert client.post(f"{url}/restore", headers=twin["headers"]).json()["status"] == "active"

    history = client.get(f"{twin['base']}/history/brands/{brand['id']}", headers=twin["headers"]).json()
    assert [h["change"] for h in history] == ["created", "updated", "archived", "restored"]
    assert [h["version"] for h in history] == [1, 2, 3, 4]
    assert history[1]["changes"] == {"positioning": ["Premium", "Café de origen"]}
    assert history[1]["reason"] == "Nuevo foco" and history[1]["actor_type"] == "user"
    assert history[2]["reason"] == "Marca retirada"
    assert history[3]["snapshot"]["status"] == "active"

    types = [e["event_type"] for e in client.get(f"{twin['base']}/timeline", headers=twin["headers"]).json()
             if e["entity_id"] == brand["id"]]
    assert types == ["entity_restored", "entity_archived", "entity_created"]


def test_nothing_is_ever_deleted(db_session, twin):
    brand = Brand(company_id=twin["id"], name="Borrable")
    db_session.add(brand)
    db_session.commit()
    db_session.delete(brand)
    with pytest.raises(TwinRuleError, match="nada se borra"):
        db_session.commit()
    db_session.rollback()


def test_validation_required_fields_choices_and_unknown_fields(client, twin):
    base = f"{twin['base']}/entities"
    assert client.post(f"{base}/brands", json={}, headers=twin["headers"]).status_code == 422
    assert client.post(f"{base}/suppliers", json={"name": "X", "criticality": "extrema"},
                       headers=twin["headers"]).status_code == 422
    assert client.post(f"{base}/brands", json={"name": "X", "hacker": 1}, headers=twin["headers"]).status_code == 422
    assert client.post(f"{base}/brands", json={"name": "X", "confidence_level": 150},
                       headers=twin["headers"]).status_code == 422
    assert client.post(f"{base}/naves", json={"name": "X"}, headers=twin["headers"]).status_code == 404


def test_references_must_stay_inside_the_same_twin(client, twin):
    dept = _create(client, twin, "departments", {"name": "Operaciones"})
    position = _create(client, twin, "positions", {"name": "Jefe de planta", "department_id": dept["id"]})
    assert position["department_id"] == dept["id"]

    other = _register(client, "otro@example.com")
    other_company = client.post("/api/v1/companies/", json={"name": "Ajena"}, headers=other).json()["id"]
    foreign = client.post(f"/api/v1/twin/{other_company}/entities/departments", json={"name": "Ajeno"},
                          headers=other).json()
    resp = client.post(f"{twin['base']}/entities/positions", json={"name": "X", "department_id": foreign["id"]},
                       headers=twin["headers"])
    assert resp.status_code == 422

    # Y otro usuario no ve nada de este Gemelo
    assert client.get(twin["base"], headers=other).status_code == 404
    assert client.get(f"{twin['base']}/entities/departments", headers=other).status_code == 404
    assert client.post(f"{twin['base']}/entities/brands", json={"name": "X"}, headers=other).status_code == 404


def test_functional_roles_are_many_to_many_with_positions_and_versioned(client, twin):
    dept = _create(client, twin, "departments", {"name": "Ventas"})
    position = _create(client, twin, "positions", {"name": "Gerente", "department_id": dept["id"]})
    r1 = _create(client, twin, "functional_roles", {"name": "Negociación"})
    r2 = _create(client, twin, "functional_roles", {"name": "Liderazgo"})
    url = f"{twin['base']}/entities/positions/{position['id']}/roles"
    resp = client.put(url, json={"functional_role_ids": [r1["id"], r2["id"]]}, headers=twin["headers"])
    assert resp.status_code == 200
    assert client.get(url, headers=twin["headers"]).json()["functional_role_ids"] == sorted([r1["id"], r2["id"]])
    history = client.get(f"{twin['base']}/history/positions/{position['id']}", headers=twin["headers"]).json()
    assert history[-1]["changes"]["functional_role_ids"][1] == sorted([r1["id"], r2["id"]])


def test_risk_is_a_transversal_property_of_existing_subjects(client, twin):
    initiative = _create(client, twin, "initiatives", {"name": "Exportar a Europa"})
    risk = _create(client, twin, "risks", {"subject_type": "initiative", "subject_id": initiative["id"],
                                           "kind": "legal",
                                           "description": "Certificación sanitaria de la UE",
                                           "severity": "alta", "probability": 0.4})
    assert risk["subject_id"] == initiative["id"]
    company_risk = _create(client, twin, "risks", {"subject_type": "company", "subject_id": twin["id"],
                                                   "kind": "financiero", "description": "Caja corta"})
    assert company_risk["subject_type"] == "company"
    bad = client.post(f"{twin['base']}/entities/risks", json={"subject_type": "process", "subject_id": "nope",
                                                               "kind": "operativo", "description": "x"},
                      headers=twin["headers"])
    assert bad.status_code == 422


# ============================================================
# Patrón A — Ciclo de Aprobación (AD-008, AD-CMP-03)
# ============================================================

def test_pattern_a_transitions_through_the_api(client, twin):
    initiative = _create(client, twin, "initiatives", {"name": "Tostadora propia"})
    assert initiative["state"] == "proposed"
    url = f"{twin['base']}/entities/initiatives/{initiative['id']}"
    assert client.patch(url, json={"state": "presented"}, headers=twin["headers"]).json()["state"] == "presented"
    assert client.patch(url, json={"state": "approved"}, headers=twin["headers"]).json()["state"] == "approved"
    # No se vuelve atrás ni se salta a un estado no permitido
    back = client.patch(url, json={"state": "proposed"}, headers=twin["headers"])
    assert back.status_code == 409 and "transición no permitida" in back.json()["detail"]
    assert client.patch(url, json={"state": "executed"}, headers=twin["headers"]).json()["state"] == "executed"

    events = [e for e in client.get(f"{twin['base']}/timeline", headers=twin["headers"]).json()
              if e["entity_id"] == initiative["id"] and e["event_type"] == "state_changed"]
    assert [(e["data"]["from"], e["data"]["to"]) for e in reversed(events)] == [
        ("proposed", "presented"), ("presented", "approved"), ("approved", "executed")]
    assert all(e["actor_type"] == "user" for e in events)


def test_an_agent_can_propose_but_never_approve_or_execute(db_session, twin):
    with acting_as(Actor.agent("CFO")):
        initiative = CompanyInitiative(company_id=twin["id"], name="Recortar costos")
        db_session.add(initiative)
        db_session.commit()
        initiative.state = "approved"
        with pytest.raises(TwinRuleError, match="solo el Usuario Principal"):
            db_session.commit()
        db_session.rollback()

        db_session.add(CompanyInitiative(company_id=twin["id"], name="Ya aprobada", state="approved"))
        with pytest.raises(TwinRuleError, match="solo puede proponer"):
            db_session.commit()
        db_session.rollback()

    # ADÁN (sistema) tampoco aprueba (AD-008 §3)
    initiative = db_session.query(CompanyInitiative).filter_by(name="Recortar costos").one()
    initiative.state = "approved"
    with pytest.raises(TwinRuleError):
        db_session.commit()
    db_session.rollback()


def test_board_room_proposal_and_client_approval_are_attributed(client, db_session, twin):
    project = db_session.query(Project).filter_by(company_id=twin["id"]).one()
    service = GemeloDigitalService(db_session)
    decision = service.propose_level_completion(project, 1, 85.0, "Listo para cerrar")
    created = db_session.query(EntityVersion).filter_by(entity_id=decision.id, version=1).one()
    assert (created.actor_type, created.actor_id) == ("agent", "Gate Review")

    resp = client.post(f"/api/v1/nivel1/{twin['id']}/decisions/{decision.id}", json={"action": "approve"},
                       headers=twin["headers"])
    assert resp.status_code == 200
    transitions = db_session.query(Event).filter_by(entity_id=decision.id, event_type="state_changed").all()
    assert [(e.data["from"], e.data["to"], e.actor_type) for e in sorted(transitions, key=lambda e: e.created_at)] == [
        ("proposed", "approved", "user"), ("approved", "executed", "user")]


# ============================================================
# Patrón B — Progreso Secuencial
# ============================================================

def test_pattern_b_levels_cannot_skip_states(db_session, twin):
    project = db_session.query(Project).filter_by(company_id=twin["id"]).one()
    level2 = db_session.query(Level).filter_by(project_id=project.id, number=2).one()
    assert level2.status == NivelStatus.BLOCKED
    level2.status = NivelStatus.COMPLETED
    with pytest.raises(TwinRuleError, match="blocked → completed"):
        db_session.commit()
    db_session.rollback()


def test_agents_only_advance_active_tasks(db_session, twin):
    project = db_session.query(Project).filter_by(company_id=twin["id"]).one()
    level1 = db_session.query(Level).filter_by(project_id=project.id, number=1).one()
    task = LevelTask(company_id=twin["id"], project_id=project.id, level_id=level1.id, title="Entrevistar 5 clientes")
    db_session.add(task)
    db_session.commit()
    with acting_as(Actor.agent("CMO")):
        task.state = "active"
        with pytest.raises(TwinRuleError, match="un Agente solo avanza"):
            db_session.commit()
        db_session.rollback()
    task.state = "active"  # el sistema la activa cuando su evidencia está completa
    db_session.commit()
    with acting_as(Actor.agent("CMO")):
        task.state = "completed"
        db_session.commit()
    assert db_session.get(LevelTask, task.id).state == "completed"


# ============================================================
# Patrón C — Registro Permanente
# ============================================================

def test_pattern_c_records_are_never_modified(client, db_session, twin):
    project = db_session.query(Project).filter_by(company_id=twin["id"]).one()
    score = Score(project_id=project.id, score_type=ScoreType.PROBLEM, value=60, confidence_level=70)
    db_session.add(score)
    db_session.commit()
    score.value = 99
    with pytest.raises(TwinRuleError, match="registro permanente"):
        db_session.commit()
    db_session.rollback()

    occurrence = _create(client, twin, "business_occurrences", {"title": "Primera venta", "nature": "fundacional"})
    resp = client.patch(f"{twin['base']}/entities/business_occurrences/{occurrence['id']}",
                        json={"title": "Otra"}, headers=twin["headers"])
    assert resp.status_code == 409
    assert db_session.get(BusinessOccurrence, occurrence["id"]).title == "Primera venta"

    event = db_session.query(Event).filter_by(company_id=twin["id"]).first()
    db_session.delete(event)
    with pytest.raises(TwinRuleError):
        db_session.commit()
    db_session.rollback()


def test_score_subject_can_be_the_responsible_user(db_session, twin):
    """AD-006 v1.2: Score del Responsable es N:1 con el Usuario Principal."""
    project = db_session.query(Project).filter_by(company_id=twin["id"]).one()
    score = Score(project_id=project.id, score_type=ScoreType.EXECUTION, value=72, confidence_level=60,
                  subject="responsible", user_id=twin["user_id"])
    db_session.add(score)
    db_session.commit()
    assert db_session.get(Score, score.id).subject == "responsible"


# ============================================================
# Patrón D — Contenedor Continuo
# ============================================================

def test_pattern_d_company_pause_and_archive(db_session, twin):
    company = db_session.get(Company, twin["id"])
    with acting_as(Actor.agent("CEO")):
        company.status = "paused"
        with pytest.raises(TwinRuleError, match="no puede pausar"):
            db_session.commit()
        db_session.rollback()
    with acting_as(Actor.user(twin["user_id"])):
        company.status = "paused"
        db_session.commit()
        company.status = "archived"
        db_session.commit()
        company.status = "active"  # archivado es terminal
        with pytest.raises(TwinRuleError, match="no permitida"):
            db_session.commit()
        db_session.rollback()


# ============================================================
# Identidad del Gemelo y Timeline
# ============================================================

def test_twin_overview_reports_identity_and_counts(client, db_session, twin):
    _create(client, twin, "brands", {"name": "Andino"})
    _create(client, twin, "competitors", {"name": "Juan Valdez",
                                          "market_id": _create(client, twin, "markets", {"name": "Cafés especiales"})["id"]})
    data = client.get(twin["base"], headers=twin["headers"]).json()
    assert data["company"]["name"] == "Café Andino"
    assert data["identity"]["lifecycle_stage"] == "nacimiento"
    assert data["counts"]["brands"] == 1 and data["counts"]["competitors"] == 1 and data["counts"]["markets"] == 1


def test_lifecycle_stage_recognizes_stagnation():
    from app.twin.api import lifecycle_stage
    assert lifecycle_stage(0.5, 0.0) == "nacimiento"
    assert lifecycle_stage(3, 0.2) == "temprana"
    assert lifecycle_stage(3, 0.5) == "crecimiento"
    assert lifecycle_stage(3, 0.8) == "madurez"
    assert lifecycle_stage(12, 0.1) == "estancamiento"  # Ley 5: Edad sin Madurez


def test_timeline_shows_domain_events_newest_first(client, db_session, twin):
    _create(client, twin, "brands", {"name": "Primera"})
    _create(client, twin, "brands", {"name": "Segunda"})
    project = db_session.query(Project).filter_by(company_id=twin["id"]).one()
    db_session.add(Event(project_id=project.id, company_id=twin["id"], event_type="memory_loaded",
                         entity_type="cognitive", entity_id="x", category="cognitive"))
    db_session.commit()
    events = client.get(f"{twin['base']}/timeline", headers=twin["headers"]).json()
    labels = [e["data"].get("label") for e in events if e["event_type"] == "entity_created"]
    assert labels[:2] == ["Segunda", "Primera"]
    assert all(e["category"] == "domain" for e in events)
    with_cognitive = client.get(f"{twin['base']}/timeline?include_cognitive=true", headers=twin["headers"]).json()
    assert any(e["category"] == "cognitive" for e in with_cognitive)


# ============================================================
# Triggers append-only en bases migradas
# ============================================================

def test_migrated_sqlite_blocks_updates_and_deletes_of_permanent_records(tmp_path):
    from sqlalchemy import create_engine
    from app.core.migrations import run_migrations

    engine = create_engine(f"sqlite:///{tmp_path}/m.db")
    run_migrations(engine)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO entity_versions (id, entity_type, entity_id, version, change, snapshot, "
                          "actor_type, created_at) VALUES ('v1', 'brands', 'b1', 1, 'created', '{}', 'system', "
                          "CURRENT_TIMESTAMP)"))
    for statement in ("UPDATE entity_versions SET change = 'x'", "DELETE FROM entity_versions"):
        with pytest.raises(Exception, match="append-only"):
            with engine.begin() as conn:
                conn.execute(text(statement))
    engine.dispose()


def test_lineage_is_append_only_in_the_orm(db_session, twin):
    other = Company(name="Hija", created_by=twin["user_id"], primary_user_id=twin["user_id"])
    db_session.add(other)
    db_session.commit()
    row = TwinLineage(company_id=other.id, source_company_id=twin["id"], relation="split_from",
                      actor_type="user", actor_id=twin["user_id"])
    db_session.add(row)
    db_session.commit()
    row.note = "editada"
    with pytest.raises(TwinRuleError):
        db_session.commit()
    db_session.rollback()


def test_decision_versions_follow_existing_nivel1_flow(client, db_session, twin):
    """El flujo de Nivel 1 (propuesta del Board → aprobación) queda versionado."""
    project = db_session.query(Project).filter_by(company_id=twin["id"]).one()
    decision = GemeloDigitalService(db_session).save_board_room_result(project, "PROCEED", 80, "Avanzar", [])
    assert decision.updated_by == "agent:Board Room"
    rows = db_session.query(EntityVersion).filter_by(entity_id=decision.id).all()
    assert [(r.version, r.change) for r in rows] == [(1, "created")]
    assert db_session.get(Decision, decision.id).status == DecisionStatus.PROPOSED


from tests.test_wo091 import fresh_pg_url, requires_pg  # noqa: E402,F401 — fixture compartida


@requires_pg
def test_migrated_postgres_blocks_updates_and_deletes_of_permanent_records(fresh_pg_url):  # noqa: F811
    from app.core.config import normalize_database_url
    from app.core.database import make_engine
    from app.core.migrations import run_migrations

    engine = make_engine(normalize_database_url(fresh_pg_url))
    run_migrations(engine)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO entity_versions (id, entity_type, entity_id, version, change, snapshot, "
                          "actor_type, created_at) VALUES ('v1', 'brands', 'b1', 1, 'created', '{}', 'system', now())"))
    for statement in ("UPDATE entity_versions SET change = 'x'", "DELETE FROM entity_versions"):
        with pytest.raises(Exception, match="append-only"):
            with engine.begin() as conn:
                conn.execute(text(statement))
    engine.dispose()
