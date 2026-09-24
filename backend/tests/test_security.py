"""Tests de seguridad — herramientas TEF, SSRF y aislamiento entre empresas (WO-094)."""
import pytest

from app.core.net import BlockedURLError, ensure_public_url
from app.models.models import Card, Conversation, Level, Project
from app.oos.models import Organization
from app.tef.interfaces import ToolContext
from app.tef.tools import (
    CalculatorTool, FileReaderTool, HttpRequestTool, PythonSandboxTool, SqlQueryTool,
)

CONTEXT = ToolContext(company_id="c", user_id="u", trace_id="t")


# ============================================================
# Herramientas TEF
# ============================================================

@pytest.mark.asyncio
async def test_calculator_rejects_sandbox_escape():
    expression = (
        "[c for c in ().__class__.__base__.__subclasses__() "
        "if c.__name__=='catch_warnings'][0]()._module.__builtins__['__import__']('os')"
    )
    result = await CalculatorTool().execute({"expression": expression}, CONTEXT)
    assert result.status == "error"


@pytest.mark.asyncio
async def test_calculator_rejects_huge_power():
    result = await CalculatorTool().execute({"expression": "(10 ** 1000) ** 1000"}, CONTEXT)
    assert result.status == "error"


@pytest.mark.asyncio
async def test_calculator_still_computes():
    result = await CalculatorTool().execute({"expression": "sum([1, 2, 3]) * -2 + sqrt(16)"}, CONTEXT)
    assert result.status == "success"
    assert result.output["result"] == -8


@pytest.mark.asyncio
@pytest.mark.parametrize("tool, params", [
    (FileReaderTool(), {"path": "/etc/hostname"}),
    (PythonSandboxTool(), {"code": "print(1)"}),
    (SqlQueryTool(), {"query": "SELECT * FROM users"}),
])
async def test_dangerous_tools_are_disabled(tool, params):
    result = await tool.execute(params, CONTEXT)
    assert result.status == "permission_denied"


# ============================================================
# SSRF
# ============================================================

@pytest.mark.asyncio
@pytest.mark.parametrize("url", [
    "http://127.0.0.1:8000/health",
    "http://localhost/",
    "http://169.254.169.254/latest/meta-data/",
    "http://10.0.0.5/",
    "http://[::1]/",
    "file:///etc/passwd",
    "ftp://example.com/",
])
async def test_internal_urls_are_blocked(url):
    with pytest.raises(BlockedURLError):
        await ensure_public_url(url)


@pytest.mark.asyncio
async def test_public_ip_is_allowed():
    await ensure_public_url("http://8.8.8.8/")


@pytest.mark.asyncio
async def test_http_tool_blocks_internal_address():
    result = await HttpRequestTool().execute({"url": "http://127.0.0.1:9/"}, CONTEXT)
    assert result.status == "error"
    assert "Blocked" in result.error


# ============================================================
# Aislamiento entre empresas
# ============================================================

def _user_headers(client, email):
    resp = client.post("/api/v1/auth/register", json={
        "email": email, "name": "User", "password": "password123",
    })
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def two_tenants(client, db_session):
    """Empresa de la víctima (con conversación) y un segundo usuario atacante."""
    victim = _user_headers(client, "victim@example.com")
    attacker = _user_headers(client, "attacker@example.com")
    company_id = client.post("/api/v1/companies/", json={"name": "Victim Corp"}, headers=victim).json()["id"]
    attacker_company_id = client.post("/api/v1/companies/", json={"name": "Attacker Corp"}, headers=attacker).json()["id"]

    project = db_session.query(Project).filter_by(company_id=company_id).one()
    level = db_session.query(Level).filter_by(project_id=project.id, number=1).one()
    card = Card(project_id=project.id, level_id=level.id, title="Dolor", card_type="pain_discovery")
    db_session.add(card)
    db_session.flush()
    conversation = Conversation(card_id=card.id)
    db_session.add(conversation)
    db_session.commit()

    return {
        "victim": victim,
        "attacker": attacker,
        "company_id": company_id,
        "attacker_company_id": attacker_company_id,
        "conversation_id": conversation.id,
    }


@pytest.mark.parametrize("resource", ["documents", "scores"])
def test_nivel1_resources_are_private(client, two_tenants, resource):
    url = f"/api/v1/nivel1/{two_tenants['company_id']}/{resource}"
    assert client.get(url, headers=two_tenants["victim"]).status_code == 200
    assert client.get(url, headers=two_tenants["attacker"]).status_code == 404


def test_chat_rejects_foreign_conversation(client, two_tenants):
    resp = client.post(
        f"/api/v1/nivel1/{two_tenants['attacker_company_id']}/chat",
        json={"message": "hola", "conversation_id": two_tenants["conversation_id"]},
        headers=two_tenants["attacker"],
    )
    assert resp.status_code == 404


def test_cognitive_rejects_foreign_conversation(client, two_tenants):
    resp = client.post(
        "/api/v1/cognitive/think",
        json={
            "message": "hola",
            "company_id": two_tenants["attacker_company_id"],
            "conversation_id": two_tenants["conversation_id"],
        },
        headers=two_tenants["attacker"],
    )
    assert resp.status_code == 404


def test_tef_execute_requires_owned_company(client, two_tenants):
    body = {"tool_id": "calculator", "params": {"expression": "6*7"}}
    own = client.post("/tef/execute", json={**body, "company_id": two_tenants["company_id"]},
                      headers=two_tenants["victim"])
    assert own.status_code == 200
    assert own.json()["output"]["result"] == 42

    foreign = client.post("/tef/execute", json={**body, "company_id": two_tenants["company_id"]},
                          headers=two_tenants["attacker"])
    assert foreign.status_code == 404
    invented = client.post("/tef/execute", json={**body, "company_id": "no-existe"},
                           headers=two_tenants["attacker"])
    assert invented.status_code == 404


def test_tef_audit_requires_owned_company(client, two_tenants):
    url = f"/tef/audit/{two_tenants['company_id']}"
    assert client.get(url, headers=two_tenants["victim"]).status_code == 200
    assert client.get(url, headers=two_tenants["attacker"]).status_code == 404


def test_tef_does_not_expose_disabled_tools(client, two_tenants):
    tool_ids = {t["id"] for t in client.get("/tef/tools").json()}
    assert tool_ids.isdisjoint({"python_sandbox", "file_reader", "sql_query"})


@pytest.fixture
def victim_org(db_session, two_tenants):
    org = Organization(company_id=two_tenants["company_id"], name="Victim Org")
    db_session.add(org)
    db_session.commit()
    return org.id


def test_oos_organization_is_private(client, two_tenants, victim_org):
    create = client.post("/oos/workorders", json={"organization_id": victim_org, "title": "Plan"},
                         headers=two_tenants["victim"])
    assert create.status_code == 200
    work_order_id = create.json()["id"]

    assert client.get(f"/oos/workorders/{victim_org}", headers=two_tenants["attacker"]).status_code == 404
    assert client.get(f"/oos/dashboard/{victim_org}", headers=two_tenants["attacker"]).status_code == 404
    assert client.post("/oos/workorders", json={"organization_id": victim_org, "title": "x"},
                       headers=two_tenants["attacker"]).status_code == 404
    assert client.patch(f"/oos/workorders/{work_order_id}", json={"status": "cancelled"},
                        headers=two_tenants["attacker"]).status_code == 404
    assert client.get(f"/oos/workorders/{victim_org}", headers=two_tenants["victim"]).status_code == 200
