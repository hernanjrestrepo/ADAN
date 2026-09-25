"""WO-099 (sprint 1): enrutamiento de modelos, Claude, salidas estructuradas y costo por empresa."""
from types import SimpleNamespace

import anthropic
import pytest

from app.ai.anthropic_adapter import AnthropicAdapter, ClaudeUnavailable, cost_usd
from app.ai.base import LLMAdapter, LLMMessage, LLMResponse
from app.ai.router import ModelRouter, tier_model
from app.ai.usage import LLMUsage, usage_scope
from app.api.v1 import nivel1 as nivel1_api
from app.core.config import settings
from app.nivel1.board_room import VOTE_SCHEMA, BoardRoom
from tests.test_wo095 import VALID_VOTE, FakeLLM, _headers

VOTE = {"analysis": "A", "justification": "J", "vote": "PIVOT", "confidence": 70,
        "key_strengths": ["s"], "key_concerns": ["c"], "questions": ["q"]}


class FakeClaude(LLMAdapter):
    """Claude de prueba: responde con salida estructurada y costo."""

    def __init__(self, tier, fail=False):
        self.tier = tier
        self.fail = fail
        self.calls = []

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
        if self.fail:
            raise anthropic.APIConnectionError(request=None)
        self.calls.append(("chat", model))
        return LLMResponse(content="respuesta de Claude", model=model, prompt_tokens=100, completion_tokens=50,
                           provider="anthropic", cost_usd=cost_usd(model, 100, 50))

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048):
        if self.fail:
            raise anthropic.APIConnectionError(request=None)
        self.calls.append(("chat_json", model))
        return LLMResponse(content="{}", model=model, prompt_tokens=1000, completion_tokens=400,
                           provider="anthropic", cost_usd=cost_usd(model, 1000, 400), parsed=dict(VOTE))

    async def generate(self, prompt, model=None, system=None, temperature=0.7, max_tokens=2048):
        return await self.chat([], model=model)

    async def health_check(self):
        return True

    def list_models(self):
        return []


def router_with_claude(fail=False):
    made = {}

    def factory(tier):
        made[tier] = FakeClaude(tier, fail=fail)
        return made[tier]
    return ModelRouter(FakeLLM(chat_replies=[VALID_VOTE]), claude_factory=factory), made


# ============================================================
# Enrutamiento
# ============================================================

@pytest.mark.asyncio
async def test_without_claude_everything_runs_on_ollama_marked_degraded():
    router = ModelRouter(FakeLLM(chat_replies=["local"]), claude_factory=lambda tier: None)
    simple = await router.chat([LLMMessage("user", "hola")])
    assert simple.content == "local" and "degraded" not in simple.metadata
    standard = await router.for_tier("standard").chat([LLMMessage("user", "hola")])
    assert standard.content == "local" and standard.metadata["degraded"] == "sin ANTHROPIC_API_KEY"


@pytest.mark.asyncio
async def test_each_tier_goes_to_its_model():
    router, made = router_with_claude()
    assert (await router.chat([LLMMessage("user", "x")])).provider != "anthropic"  # simple: Ollama
    await router.for_tier("standard").chat([LLMMessage("user", "x")])
    await router.for_tier("complex").chat_json([LLMMessage("user", "x")], VOTE_SCHEMA)
    assert made["standard"].calls == [("chat", settings.LLM_MODEL_STANDARD)]
    assert made["complex"].calls == [("chat_json", settings.LLM_MODEL_COMPLEX)]
    assert tier_model("fast") == settings.LLM_MODEL_FAST and tier_model("simple") == settings.DEFAULT_MODEL


@pytest.mark.asyncio
async def test_claude_failure_degrades_to_ollama():
    router, _ = router_with_claude(fail=True)
    response = await router.for_tier("complex").chat([LLMMessage("user", "x")])
    assert response.content == VALID_VOTE
    assert response.metadata["degraded"] == "Claude no disponible (APIConnectionError)"


def test_unknown_tier_is_rejected():
    router, _ = router_with_claude()
    with pytest.raises(ValueError):
        router.for_tier("mágico")


# ============================================================
# Adaptador de Anthropic
# ============================================================

class FakeMessages:
    def __init__(self, message):
        self.message = message
        self.params = None

    async def create(self, **params):
        self.params = params
        return self.message


def claude_message(text, stop_reason="end_turn", model="claude-opus-5"):
    return SimpleNamespace(content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
                           model=model, stop_reason=stop_reason,
                           usage=SimpleNamespace(input_tokens=2000, output_tokens=1000))


@pytest.mark.asyncio
async def test_anthropic_structured_output_request_and_cost():
    messages = FakeMessages(claude_message('{"vote": "STOP"}'))
    adapter = AnthropicAdapter(api_key="k", default_model="claude-opus-5", effort="medium",
                               client=SimpleNamespace(messages=messages))
    response = await adapter.chat_json([LLMMessage("system", "Eres el CFO"), LLMMessage("user", "Analiza")],
                                       VOTE_SCHEMA, max_tokens=1500)
    params = messages.params
    assert params["system"] == "Eres el CFO"
    assert params["messages"] == [{"role": "user", "content": "Analiza"}]
    assert "temperature" not in params  # los modelos actuales rechazan el muestreo
    assert params["output_config"] == {"effort": "medium", "format": {"type": "json_schema", "schema": VOTE_SCHEMA}}
    assert params["extra_body"] == {"fallbacks": "default"}
    assert params["max_tokens"] >= 8000  # margen para el pensamiento adaptativo
    assert response.parsed == {"vote": "STOP"} and response.provider == "anthropic"
    assert response.cost_usd == pytest.approx((2000 * 5 + 1000 * 25) / 1_000_000)


@pytest.mark.asyncio
async def test_anthropic_refusal_raises_so_the_router_degrades():
    adapter = AnthropicAdapter(api_key="k", client=SimpleNamespace(messages=FakeMessages(claude_message("", "refusal"))))
    with pytest.raises(ClaudeUnavailable):
        await adapter.chat([LLMMessage("user", "x")])


def test_haiku_gets_no_effort_and_cost_uses_served_model():
    adapter = AnthropicAdapter(api_key="k", default_model="claude-haiku-4-5", effort="low",
                               client=SimpleNamespace(messages=None))
    assert "output_config" not in adapter._params([LLMMessage("user", "x")], "claude-haiku-4-5", 100)
    assert cost_usd("claude-sonnet-5", 1_000_000, 0) == 2.0
    assert cost_usd("modelo-desconocido", 10, 10) == 0.0


# ============================================================
# Board Room con salida estructurada y costo por empresa
# ============================================================

@pytest.mark.asyncio
async def test_board_uses_structured_output_on_complex_tier():
    router, made = router_with_claude()
    consensus = await BoardRoom(router).run("Los restaurantes pierden inventario")
    assert {v.vote for v in consensus.votes} == {"PIVOT"} and consensus.decision == "PIVOT"
    assert len(made["complex"].calls) == 4 and all(c[0] == "chat_json" for c in made["complex"].calls)


@pytest.mark.asyncio
async def test_local_structured_output_parses_json():
    consensus = await BoardRoom(FakeLLM(chat_replies=[VALID_VOTE])).run("Problema")
    assert consensus.decision == "PROCEED" and all(v.vote == "PROCEED" for v in consensus.votes)


def test_usage_scope_persists_calls_for_the_company(db_session, client):
    headers = _headers(client, "wo099@example.com")
    company_id = client.post("/api/v1/companies/", json={"name": "Costos SAS"}, headers=headers).json()["id"]
    router, _ = router_with_claude()
    client.app.dependency_overrides[nivel1_api.get_llm] = lambda: router

    assert client.post(f"/api/v1/nivel1/{company_id}/chat", json={"message": "Pierdo inventario cada semana"},
                       headers=headers).status_code == 200
    assert client.post(f"/api/v1/nivel1/{company_id}/board-room", headers=headers).status_code == 200

    rows = db_session.query(LLMUsage).filter(LLMUsage.company_id == company_id).all()
    assert {(r.tier, r.provider) for r in rows} == {("standard", "anthropic"), ("complex", "anthropic")}
    assert all(r.level_number == 1 for r in rows)

    summary = client.get(f"/api/v1/companies/{company_id}/llm-usage", headers=headers).json()
    assert summary["calls"] == len(rows) == 5  # 1 conversación + 4 votos del Board
    assert summary["cost_usd"] == pytest.approx(sum(r.cost_usd for r in rows), abs=1e-6)
    assert set(summary["by_model"]) == {f"anthropic:{settings.LLM_MODEL_STANDARD}",
                                        f"anthropic:{settings.LLM_MODEL_COMPLEX}"}
    # Aislamiento: otra persona no ve los costos
    other = _headers(client, "otro099@example.com")
    assert client.get(f"/api/v1/companies/{company_id}/llm-usage", headers=other).status_code == 404


def test_usage_scope_saves_records_even_if_the_request_fails(db_session, client):
    headers = _headers(client, "wo099b@example.com")
    company_id = client.post("/api/v1/companies/", json={"name": "Falla SAS"}, headers=headers).json()["id"]
    response = LLMResponse(content="x", model="m", provider="anthropic", cost_usd=0.5)
    from app.ai.usage import record_usage
    with pytest.raises(RuntimeError):
        with usage_scope(db_session, company_id, level=2):
            record_usage(response, "complex", "chat")
            raise RuntimeError("falló después de llamar al modelo")
    row = db_session.query(LLMUsage).filter(LLMUsage.company_id == company_id).one()
    assert row.cost_usd == 0.5 and row.level_number == 2
