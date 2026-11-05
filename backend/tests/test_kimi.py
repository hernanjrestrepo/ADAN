"""Kimi (Moonshot) como proveedor de nube: elección por configuración, llamadas y caída a Ollama."""
import json

import httpx
import pytest

from app.ai.base import LLMMessage
from app.ai.kimi_adapter import KIMI_TEMPERATURE, KimiAdapter
from app.ai.router import ModelRouter, cloud_provider, tier_model
from app.core.config import settings
from tests.test_wo095 import FakeLLM


@pytest.fixture
def kimi_settings(monkeypatch):
    monkeypatch.setattr(settings, "LLM_CLOUD_PROVIDER", "kimi")
    monkeypatch.setattr(settings, "KIMI_API_KEY", "sk-prueba")
    monkeypatch.setattr(settings, "KIMI_MODEL", "kimi-k2.6")


def _client(reply: str, seen: list):
    def handler(request: httpx.Request):
        seen.append(json.loads(request.content))
        return httpx.Response(200, json={"model": "kimi-k2.6", "choices": [
            {"message": {"content": reply}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1000, "completion_tokens": 500}})
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_provider_choice(monkeypatch):
    monkeypatch.setattr(settings, "KIMI_API_KEY", "sk-prueba")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "sk-ant")
    monkeypatch.setattr(settings, "LLM_CLOUD_PROVIDER", "auto")
    assert cloud_provider() == "anthropic"
    monkeypatch.setattr(settings, "LLM_CLOUD_PROVIDER", "kimi")
    assert cloud_provider() == "kimi" and tier_model("complex") == "kimi-k2.6"
    assert tier_model("simple") == settings.DEFAULT_MODEL
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(settings, "LLM_CLOUD_PROVIDER", "auto")
    assert cloud_provider() == "kimi"
    monkeypatch.setattr(settings, "KIMI_API_KEY", "")
    assert cloud_provider() is None


@pytest.mark.asyncio
async def test_chat_and_cost(kimi_settings):
    seen = []
    kimi = KimiAdapter(client=_client("hola", seen))
    r = await kimi.chat([LLMMessage("system", "s"), LLMMessage("user", "u")], temperature=0.2)
    assert r.content == "hola" and r.provider == "kimi"
    # Sin razonamiento, Kimi solo acepta temperatura 0.6
    assert seen[0]["temperature"] == KIMI_TEMPERATURE and seen[0]["thinking"] == {"type": "disabled"}
    assert r.cost_usd == pytest.approx((1000 * 0.95 + 500 * 4.0) / 1_000_000)


@pytest.mark.asyncio
async def test_chat_json_parses_and_sends_schema(kimi_settings):
    seen = []
    kimi = KimiAdapter(client=_client('{"vote": "PIVOT"}', seen))
    r = await kimi.chat_json([LLMMessage("user", "u")], {"type": "object"})
    assert r.parsed == {"vote": "PIVOT"}
    assert seen[0]["response_format"] == {"type": "json_object"} and "esquema" in seen[0]["messages"][-1]["content"]
    bad = await KimiAdapter(client=_client("no es json", [])).chat_json([LLMMessage("user", "u")], {})
    assert bad.parsed is None


@pytest.mark.asyncio
async def test_router_uses_kimi_and_degrades_with_its_name(kimi_settings, monkeypatch):
    def failing(request):
        return httpx.Response(400, json={"error": "sin saldo"})
    monkeypatch.setattr(KimiAdapter, "_http", lambda self: httpx.AsyncClient(transport=httpx.MockTransport(failing)))
    router = ModelRouter(FakeLLM(chat_replies=["local"]))
    r = await router.for_tier("standard").chat([LLMMessage("user", "u")])
    assert r.content == "local" and r.metadata["degraded"] == "Kimi no disponible (HTTP 400: sin saldo)"


def test_failure_reason_shows_the_provider_message_or_the_error_type():
    from app.ai.router import failure_reason

    def status_error(status, body):
        request = httpx.Request("POST", "https://x/chat/completions")
        return httpx.HTTPStatusError("x", request=request, response=httpx.Response(status, json=body, request=request))

    assert failure_reason(status_error(401, {"error": {"message": "Invalid API key"}})) == "HTTP 401: Invalid API key"
    assert failure_reason(status_error(404, {"error": {"message": "No endpoints found for kimi-k2.6"}})).startswith("HTTP 404")
    assert failure_reason(status_error(500, {})) == "HTTP 500"
    assert failure_reason(RuntimeError("x")) == "RuntimeError"


# ============================================================
# OpenRouter
# ============================================================

@pytest.fixture
def openrouter_settings(monkeypatch):
    monkeypatch.setattr(settings, "LLM_CLOUD_PROVIDER", "openrouter")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(settings, "KIMI_API_KEY", "")
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.setattr(settings, "OPENROUTER_MODEL", "moonshotai/test-model")


def test_openrouter_is_chosen_explicitly_or_as_the_last_option_in_auto(monkeypatch):
    from app.ai.router import cloud_provider
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(settings, "KIMI_API_KEY", "")
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "sk-or-x")
    monkeypatch.setattr(settings, "LLM_CLOUD_PROVIDER", "auto")
    assert cloud_provider() == "openrouter"
    monkeypatch.setattr(settings, "KIMI_API_KEY", "k")
    assert cloud_provider() == "kimi"  # Kimi pesa más que OpenRouter en auto
    monkeypatch.setattr(settings, "LLM_CLOUD_PROVIDER", "openrouter")
    assert cloud_provider() == "openrouter"
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "")
    assert cloud_provider() is None


@pytest.mark.asyncio
async def test_openrouter_sends_its_own_key_model_and_reasoning_setting(openrouter_settings):
    from app.ai.kimi_adapter import OpenRouterAdapter
    seen, headers = [], []

    def handler(request):
        seen.append(json.loads(request.content))
        headers.append((str(request.url), request.headers["authorization"]))
        return httpx.Response(200, json={"model": "moonshotai/test-model", "choices": [{"message": {"content": "hola"}}],
                                         "usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.00123}})
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    r = await OpenRouterAdapter(client=client).chat([LLMMessage("user", "u")])
    assert r.content == "hola" and r.provider == "openrouter" and r.cost_usd == pytest.approx(0.00123)
    assert headers[0] == ("https://openrouter.ai/api/v1/chat/completions", "Bearer sk-or-test")
    assert seen[0]["model"] == "moonshotai/test-model"
    assert seen[0]["reasoning"] == {"enabled": False} and "thinking" not in seen[0]


@pytest.mark.asyncio
async def test_openrouter_estimates_the_cost_when_the_response_has_none(openrouter_settings, monkeypatch):
    from app.ai.kimi_adapter import OpenRouterAdapter
    monkeypatch.setattr(settings, "OPENROUTER_PRICE_INPUT", 1.0)
    monkeypatch.setattr(settings, "OPENROUTER_PRICE_OUTPUT", 2.0)
    client = httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(
        200, json={"choices": [{"message": {"content": "x"}}], "usage": {"prompt_tokens": 1000, "completion_tokens": 500}})))
    r = await OpenRouterAdapter(client=client).chat([LLMMessage("user", "u")])
    assert r.cost_usd == pytest.approx(0.002)


@pytest.mark.asyncio
async def test_router_uses_openrouter_without_web_search_and_degrades_with_its_name(openrouter_settings, monkeypatch):
    from app.ai.kimi_adapter import OpenRouterAdapter
    calls = []

    def ok(request):
        calls.append(json.loads(request.content)["model"])
        return httpx.Response(200, json={"choices": [{"message": {"content": "de la nube"}}], "usage": {}})
    monkeypatch.setattr(OpenRouterAdapter, "_http", lambda self: httpx.AsyncClient(transport=httpx.MockTransport(ok)))
    router = ModelRouter(FakeLLM(chat_replies=["local"]))
    view = router.for_tier("standard")
    assert (await view.chat([LLMMessage("user", "u")])).content == "de la nube" and calls == ["moonshotai/test-model"]
    searched = await view.chat_search([LLMMessage("user", "u")])
    assert searched.metadata["searched"] is False  # OpenRouter no tiene búsqueda integrada

    def failing(request):
        return httpx.Response(404, json={"error": {"message": "No endpoints found for moonshotai/test-model"}})
    monkeypatch.setattr(OpenRouterAdapter, "_http", lambda self: httpx.AsyncClient(transport=httpx.MockTransport(failing)))
    r = await router.for_tier("standard").chat([LLMMessage("user", "u")])
    assert r.metadata["degraded"] == "OpenRouter no disponible (HTTP 404: No endpoints found for moonshotai/test-model)"


def test_vision_uses_openrouter_when_it_is_the_provider(openrouter_settings):
    from app.documents import media
    base, key, model, reasoning = media._vision()
    assert base == "https://openrouter.ai/api/v1" and key == "sk-or-test" and model == "moonshotai/test-model"
    assert reasoning == {"reasoning": {"enabled": False}} and media.can_see()
