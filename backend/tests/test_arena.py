"""La Arena: cuatro inversionistas simulados; se pasa con 2 respaldos y ninguna falla fatal."""
import json

from app.ai.base import LLMAdapter, LLMResponse
from app.arena.service import INVESTORS
from tests.test_discovery import _setup, _use

QUESTIONS = {"first_impression": "Mercado grande, cero ventas.", "questions": ["¿Cuánto cuesta adquirir un cliente?",
             "¿Quién ya te pagó?"], "red_flags": ["Sin tracción"]}


def decision(kind, fatal=""):
    return {"decision": kind, "amount_usd": 100000 if kind != "NO_INVIERTE" else 0, "terms": "10 % por USD 100.000",
            "reason": "Razón concreta.", "conditions": ["20 ventas reales"], "fatal_flaw": fatal}


class InvestorsLLM(LLMAdapter):
    """Cada inversionista responde según su nombre en el sistema; la primera ronda son preguntas."""

    def __init__(self, decisions, degraded_for=None):
        self.decisions, self.degraded_for, self.prompts = decisions, degraded_for, []

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048):
        system, prompt = messages[0].content, messages[1].content
        self.prompts.append(prompt)
        inv = next(i for i in INVESTORS if i["name"] in system)
        data = QUESTIONS if "decision" not in schema["properties"] else self.decisions[inv["id"]]
        resp = LLMResponse(content=json.dumps(data), model="fake", parsed=data)
        if self.degraded_for == inv["id"] and "decision" in schema["properties"]:
            resp.metadata["degraded"] = "Kimi no disponible"
        return resp

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
        raise AssertionError

    async def generate(self, prompt, model=None, system=None, temperature=0.7, max_tokens=2048):
        raise AssertionError

    async def health_check(self):
        return True

    def list_models(self):
        return []


def _enter(client, email, decisions, **kw):
    cid, headers = _setup(client, email)
    llm = _use(client, InvestorsLLM(decisions, **kw))
    start = client.post(f"/api/v1/nivel1/{cid}/arena/start", json={"pitch": "Pan de masa madre por suscripción"},
                        headers=headers)
    assert start.status_code == 200, start.text
    return cid, headers, llm, start.json()


def test_the_arena_asks_then_decides_and_passes_with_two_backers(client):
    decisions = {"angel": decision("INVIERTE"), "vc": decision("NO_INVIERTE"), "banca": decision("CON_CONDICIONES"),
                 "estrategico": decision("NO_INVIERTE")}
    cid, headers, llm, session = _enter(client, "arena@example.com", decisions)
    assert session["phase"] == "questions" and len(session["investors"]) == 4
    assert session["investors"][0]["questions"] == QUESTIONS["questions"]
    assert "Pan de masa madre" in llm.prompts[0]

    answers = {"angel": "Ya vendí 30 suscripciones en mi conjunto", "vc": "CAC de USD 8 en la prueba"}
    done = client.post(f"/api/v1/nivel1/{cid}/arena/{session['id']}/answer", json={"answers": answers},
                       headers=headers).json()
    assert done["passed"] is True and done["backers"] == 2 and done["total_usd"] == 200000
    assert "Pasaste La Arena" in done["verdict"]
    # Cada inversionista leyó la respuesta que le dieron
    assert any("Ya vendí 30 suscripciones" in p for p in llm.prompts[4:])
    assert client.get(f"/api/v1/nivel1/{cid}/arena/last", headers=headers).json()["id"] == session["id"]
    # Una sesión terminada no se vuelve a responder
    again = client.post(f"/api/v1/nivel1/{cid}/arena/{session['id']}/answer", json={"answers": {}}, headers=headers)
    assert again.status_code == 409


def test_a_fatal_flaw_blocks_the_arena_even_with_backers(client):
    decisions = {"angel": decision("INVIERTE"), "vc": decision("INVIERTE"), "banca": decision("CON_CONDICIONES"),
                 "estrategico": decision("NO_INVIERTE", fatal="Opera sin el registro sanitario obligatorio")}
    cid, headers, _, session = _enter(client, "arenafatal@example.com", decisions)
    done = client.post(f"/api/v1/nivel1/{cid}/arena/{session['id']}/answer", json={"answers": {}}, headers=headers).json()
    assert done["passed"] is False and "1 de 4 ven una falla fatal (Grupo Estratégico)" in done["verdict"]
    strategic = next(i for i in done["investors"] if i["id"] == "estrategico")
    assert "registro sanitario" in strategic["fatal_flaw"] and strategic["conditions"] == []


def test_one_backer_is_not_enough(client):
    decisions = {"angel": decision("INVIERTE"), "vc": decision("NO_INVIERTE"), "banca": decision("NO_INVIERTE"),
                 "estrategico": decision("NO_INVIERTE")}
    cid, headers, _, session = _enter(client, "arenauno@example.com", decisions)
    done = client.post(f"/api/v1/nivel1/{cid}/arena/{session['id']}/answer", json={"answers": {}}, headers=headers).json()
    assert done["passed"] is False and "solo 1 de 4" in done["verdict"]


def test_an_investor_that_did_not_answer_never_counts_as_a_decision(client):
    decisions = {i["id"]: decision("INVIERTE") for i in INVESTORS}
    cid, headers, _, session = _enter(client, "arenadeg@example.com", decisions, degraded_for="vc")
    done = client.post(f"/api/v1/nivel1/{cid}/arena/{session['id']}/answer", json={"answers": {}}, headers=headers).json()
    vc = next(i for i in done["investors"] if i["id"] == "vc")
    assert vc["decision"] == "SIN_RESPUESTA" and done["passed"] is False


def test_the_arena_needs_something_to_evaluate(client):
    cid, headers = _setup(client, "arenavacia@example.com")
    _use(client, InvestorsLLM({}))
    resp = client.post(f"/api/v1/nivel1/{cid}/arena/start", json={}, headers=headers)
    assert resp.status_code == 400


def test_the_arena_of_another_company_is_off_limits(client):
    cid, _ = _setup(client, "arenaduena@example.com")
    _, other = _setup(client, "arenaintrusa@example.com")
    _use(client, InvestorsLLM({}))
    assert client.post(f"/api/v1/nivel1/{cid}/arena/start", json={"pitch": "x"}, headers=other).status_code == 404
