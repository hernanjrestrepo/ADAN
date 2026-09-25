"""Adaptador de Anthropic (WO-099): modelos Claude por la API oficial.

- Sin parámetros de muestreo: los modelos actuales (Opus 5, Sonnet 5) los rechazan.
- Pensamiento adaptativo por defecto; el esfuerzo (`effort`) se fija por nivel de complejidad.
- `chat_json` usa salidas estructuradas (`output_config.format`): la respuesta cumple el esquema.
- `fallbacks: "default"`: si el modelo declina por política, la API reintenta con el modelo
  que Anthropic recomienda para esa categoría.
- Costo de cada llamada según la tarifa pública por millón de tokens.
"""
from __future__ import annotations

import json
import time
from typing import AsyncGenerator

import anthropic

from app.ai.base import LLMAdapter, LLMMessage, LLMResponse
from app.core.config import settings

# USD por millón de tokens (entrada, salida)
PRICES: dict[str, tuple[float, float]] = {
    "claude-opus-5": (5.0, 25.0),
    "claude-opus-5-5": (4.0, 20.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-haiku-4-5": (1.0, 5.0),
}
FALLBACK_BETA = "server-side-fallback-2026-07-01"
# Modelos que aceptan `effort` (Haiku 4.5 no)
EFFORT_MODELS = ("claude-opus", "claude-sonnet-5", "claude-fable")


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    price_in, price_out = next((p for m, p in PRICES.items() if model.startswith(m)), (0.0, 0.0))
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000


class ClaudeUnavailable(RuntimeError):
    """Claude no produjo respuesta útil (rechazo o respuesta vacía): el enrutador degrada."""


class AnthropicAdapter(LLMAdapter):
    def __init__(self, api_key: str | None = None, default_model: str | None = None,
                 effort: str | None = None, client: anthropic.AsyncAnthropic | None = None):
        self._client = client or anthropic.AsyncAnthropic(
            api_key=api_key or settings.ANTHROPIC_API_KEY, timeout=settings.AI_TIMEOUT_SECONDS, max_retries=2,
        )
        self._default_model = default_model or settings.LLM_MODEL_STANDARD
        self._effort = effort

    def _params(self, messages: list[LLMMessage], model: str, max_tokens: int) -> dict:
        system = "\n\n".join(m.content for m in messages if m.role == "system")
        params: dict = {
            "model": model,
            # Con pensamiento adaptativo el presupuesto de salida incluye el razonamiento
            "max_tokens": max(max_tokens * 4, 8000),
            "messages": [{"role": m.role, "content": m.content} for m in messages if m.role != "system"],
            "extra_headers": {"anthropic-beta": FALLBACK_BETA},
            "extra_body": {"fallbacks": "default"},
        }
        if system:
            params["system"] = system
        if self._effort and model.startswith(EFFORT_MODELS):
            params["output_config"] = {"effort": self._effort}
        return params

    def _to_response(self, message, requested_model: str, start: float) -> LLMResponse:
        if message.stop_reason == "refusal":
            raise ClaudeUnavailable("Claude declinó la solicitud")
        text = "".join(block.text for block in message.content if block.type == "text")
        served = message.model or requested_model
        usage = message.usage
        return LLMResponse(
            content=text,
            model=served,
            prompt_tokens=usage.input_tokens,
            completion_tokens=usage.output_tokens,
            duration_s=time.monotonic() - start,
            done=message.stop_reason != "max_tokens",
            metadata={"stop_reason": message.stop_reason},
            provider="anthropic",
            cost_usd=cost_usd(served, usage.input_tokens, usage.output_tokens),
        )

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048) -> LLMResponse:
        model = model or self._default_model
        start = time.monotonic()
        message = await self._client.messages.create(**self._params(messages, model, max_tokens))
        return self._to_response(message, model, start)

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048) -> LLMResponse:
        model = model or self._default_model
        params = self._params(messages, model, max_tokens)
        params["output_config"] = {**params.get("output_config", {}),
                                   "format": {"type": "json_schema", "schema": schema}}
        start = time.monotonic()
        message = await self._client.messages.create(**params)
        response = self._to_response(message, model, start)
        try:
            response.parsed = json.loads(response.content)
        except json.JSONDecodeError:
            response.parsed = None
        return response

    async def chat_stream(self, messages, model=None, temperature=0.7, max_tokens=2048) -> AsyncGenerator[str, None]:
        model = model or self._default_model
        async with self._client.messages.stream(**self._params(messages, model, max_tokens)) as stream:
            async for text in stream.text_stream:
                yield text
            final = await stream.get_final_message()
        self.last_stream_response = self._to_response(final, model, time.monotonic())

    async def generate(self, prompt, model=None, system=None, temperature=0.7, max_tokens=2048) -> LLMResponse:
        messages = ([LLMMessage("system", system)] if system else []) + [LLMMessage("user", prompt)]
        return await self.chat(messages, model=model, max_tokens=max_tokens)

    async def health_check(self) -> bool:
        return bool(settings.ANTHROPIC_API_KEY)

    def list_models(self) -> list[str]:
        return list(PRICES)
