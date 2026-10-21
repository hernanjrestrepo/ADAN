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
    assert r.content == "local" and r.metadata["degraded"] == "Kimi no disponible (HTTPStatusError)"
