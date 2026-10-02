"""WO-109 — Agentes por tiempo: catálogo, contratación por período, tareas como Work Orders, TEF y medición."""
import json

import pytest

from app.ai.base import LLMResponse
from app.api.v1 import nivel1 as nivel1_api
from app.hire.models import AgentWorkLog
from app.oos.models import Assignment, Organization, WorkOrder
from app.tef.models import ToolAuditEntry
from app.twin.hooks import TwinRuleError


class HireLLM:
    """Simula al agente: puede pedir una herramienta (chat_json) y luego entrega (chat)."""

    def __init__(self, plan=None, answer="Entrega del agente", fail=False):
        self.plan = plan or {"tool": "none", "params": {}, "reason": "no hace falta"}
        self.answer, self.fail, self.seen = answer, fail, []

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048):
        return LLMResponse(content=json.dumps(self.plan), model="fake")

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
        self.seen.append(messages[-1].content)
        if self.fail:
            raise RuntimeError("modelo caído")
        return LLMResponse(content=self.answer, model="fake")


def _register(client, email):
    resp = client.post("/api/v1/auth/register", json={"email": email, "name": "U", "password": "password123",
                                                      "accept_data_policy": True})
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def co(client):
    headers = _register(client, "hire@example.com")
    cid = client.post("/api/v1/companies/", json={"name": "Xmart Travel", "industry": "Turismo"},
                      headers=headers).json()["id"]
    return {"id": cid, "headers": headers, "base": f"/api/v1/hire/{cid}"}


@pytest.fixture
def use_llm(client):
    def install(llm):
        client.app.dependency_overrides[nivel1_api.get_llm] = lambda: llm
        return llm
    return install


def _hire(client, co, code="redactor", period="week", units=2):
    resp = client.post(f"{co['base']}/contracts", json={"offering_code": code, "period": period, "units": units},
                       headers=co["headers"])
    assert resp.status_code == 201, resp.text
    return resp.json()


def _task(client, co, contract, title="Escribir la propuesta de valor"):
    resp = client.post(f"{co['base']}/contracts/{contract['id']}/tasks",
                       json={"title": title, "description": "Para viajeros de negocios"}, headers=co["headers"])
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_catalog_lists_hireable_agents_without_inventing_prices(client, co):
    items = client.get("/api/v1/hire/catalog", headers=co["headers"]).json()
    assert {i["code"] for i in items} == {"investigador", "analista_financiero", "redactor", "asistente_operaciones"}
    assert all(i["price_note"] == "Precio por definir (WO-100)" for i in items)
    assert next(i for i in items if i["code"] == "analista_financiero")["tools"] == ["calculator"]


def test_hiring_by_period_sets_capacity_in_work_hours(client, co):
    week = _hire(client, co, period="week", units=2)
    assert week["hours_capacity"] == 80 and week["hours_used"] == 0 and week["state"] == "active"
    assert _hire(client, co, period="hour", units=5)["hours_capacity"] == 5
    assert _hire(client, co, period="month", units=1)["hours_capacity"] == 160
    for body in ({"offering_code": "redactor", "period": "year", "units": 1},
                 {"offering_code": "redactor", "period": "month", "units": 13},
                 {"offering_code": "no-existe", "period": "day", "units": 1}):
        assert client.post(f"{co['base']}/contracts", json=body, headers=co["headers"]).status_code == 422


def test_tasks_are_oos_work_orders_assigned_to_the_agent(client, db_session, co):
    contract = _hire(client, co)
    task = _task(client, co, contract)
    wo = db_session.get(WorkOrder, task["id"])
    org = db_session.get(Organization, wo.organization_id)
    assert org.company_id == co["id"]
    assert wo.assigned_to == contract["id"] and wo.metadata_json["source"] == "hire"
    assignment = db_session.query(Assignment).filter_by(work_order_id=wo.id).one()
    assert assignment.assigned_to_type == "agent" and assignment.assigned_to_name == "Redactor Comercial"


def test_agent_uses_a_tef_tool_and_the_work_is_measured(client, db_session, co, use_llm):
    llm = use_llm(HireLLM(plan={"tool": "calculator", "params": {"expression": "1500*12"}, "reason": "ingreso anual"},
                          answer="Ingreso anual estimado: 18.000 USD"))
    contract = _hire(client, co, code="analista_financiero", period="day", units=1)
    task = _task(client, co, contract, title="Proyectar el ingreso anual")
    resp = client.post(f"{co['base']}/contracts/{contract['id']}/tasks/{task['id']}/run", headers=co["headers"])
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["task"]["status"] == "review" and "18.000" in body["task"]["result"]
    assert body["work"]["tools_used"] == [{"tool": "calculator", "status": "success"}]
    assert body["work"]["seconds"] >= 0 and body["work"]["outcome"] == "delivered"
    assert "18000" in llm.seen[-1]  # el resultado de la herramienta llega al agente
    audit = db_session.query(ToolAuditEntry).filter_by(company_id=co["id"], tool_id="calculator").all()
    assert audit and audit[-1].status == "success"


def test_client_reviews_and_corrections_reach_the_next_run(client, co, use_llm):
    llm = use_llm(HireLLM(answer="Primera versión"))
    contract = _hire(client, co)
    task = _task(client, co, contract)
    base = f"{co['base']}/contracts/{contract['id']}/tasks/{task['id']}"
    client.post(f"{base}/run", headers=co["headers"])
    assert client.post(f"{base}/run", headers=co["headers"]).status_code == 409  # ya entregada
    assert client.post(f"{base}/review", json={"approve": False}, headers=co["headers"]).status_code == 409
    back = client.post(f"{base}/review", json={"approve": False, "feedback": "Más corto y con precio"},
                       headers=co["headers"]).json()
    assert back["status"] == "assigned" and back["feedback"] == ["Más corto y con precio"]
    client.post(f"{base}/run", headers=co["headers"])
    assert "Más corto y con precio" in llm.seen[-1]
    done = client.post(f"{base}/review", json={"approve": True}, headers=co["headers"]).json()
    assert done["status"] == "completed" and done["completed_at"]


def test_a_failed_run_is_recorded_and_the_task_stays_open(client, db_session, co, use_llm):
    use_llm(HireLLM(fail=True))
    contract = _hire(client, co)
    task = _task(client, co, contract)
    body = client.post(f"{co['base']}/contracts/{contract['id']}/tasks/{task['id']}/run",
                       headers=co["headers"]).json()
    assert body["work"]["outcome"] == "failed" and body["task"]["status"] == "assigned"
    assert "No se pudo completar" in body["task"]["blocking_reason"]
    assert db_session.query(AgentWorkLog).count() == 1


def test_capacity_and_cancellation_stop_new_work(client, db_session, co, use_llm):
    use_llm(HireLLM())
    contract = _hire(client, co, period="hour", units=1)
    task = _task(client, co, contract)
    from datetime import datetime, timezone
    db_session.add(AgentWorkLog(contract_id=contract["id"], work_order_id=task["id"], seconds=3600,
                                started_at=datetime.now(timezone.utc), outcome="delivered"))
    db_session.commit()
    assert client.get(f"{co['base']}/contracts", headers=co["headers"]).json()[0]["state"] == "exhausted"
    assert client.post(f"{co['base']}/contracts/{contract['id']}/tasks/{task['id']}/run",
                       headers=co["headers"]).status_code == 409
    assert client.post(f"{co['base']}/contracts/{contract['id']}/tasks", json={"title": "Otra tarea más"},
                       headers=co["headers"]).status_code == 409

    other = _hire(client, co)
    cancelled = client.post(f"{co['base']}/contracts/{other['id']}/cancel", headers=co["headers"]).json()
    assert cancelled["state"] == "cancelled"
    assert client.post(f"{co['base']}/contracts/{other['id']}/tasks", json={"title": "Tarea tras cancelar"},
                       headers=co["headers"]).status_code == 409


def test_work_logs_are_append_only(client, db_session, co, use_llm):
    use_llm(HireLLM())
    contract = _hire(client, co)
    task = _task(client, co, contract)
    client.post(f"{co['base']}/contracts/{contract['id']}/tasks/{task['id']}/run", headers=co["headers"])
    log = db_session.query(AgentWorkLog).one()
    log.outcome = "failed"  # cambiar la constancia de una entrega no está permitido
    with pytest.raises(TwinRuleError):
        db_session.flush()
    db_session.rollback()


def test_report_to_the_client(client, co, use_llm):
    use_llm(HireLLM())
    contract = _hire(client, co, period="day", units=1)
    for title in ("Primera tarea de prueba", "Segunda tarea de prueba"):
        task = _task(client, co, contract, title=title)
        client.post(f"{co['base']}/contracts/{contract['id']}/tasks/{task['id']}/run", headers=co["headers"])
    report = client.get(f"{co['base']}/contracts/{contract['id']}/report", headers=co["headers"]).json()
    assert report["hours_capacity"] == 8 and report["runs"] == 2 and report["delivered"] == 2
    assert report["tasks"]["review"] == 2 and report["state"] == "active"
    assert report["price_note"] == "Precio por definir (WO-100)"


def test_contracts_are_private(client, co):
    contract = _hire(client, co)
    other = _register(client, "otro@example.com")
    assert client.get(f"{co['base']}/contracts", headers=other).status_code == 404
    assert client.get(f"{co['base']}/contracts/{contract['id']}/report", headers=other).status_code == 404
