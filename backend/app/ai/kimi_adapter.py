"""Adaptador de Kimi (Moonshot): la misma cuenta que usa Xmart Travel, por su API compatible con OpenAI.

- Razonamiento largo apagado (`thinking: disabled`) para responder en segundos; así Kimi solo acepta
  temperatura 0.6 (cualquier otra devuelve 400), igual que en Xmart (`xmart/agentes/gateway.py`).
- `chat_json` pide `response_format: json_object` y pone el esquema en las instrucciones: Moonshot no
  valida el esquema, así que la respuesta se parsea y, si no es JSON, `parsed` queda en None.
- Costo de cada llamada según la tarifa de lista por millón de tokens (`KIMI_PRICE_*`).
"""
from __future__ import annotations

import json
import time
from typing import AsyncGenerator

import httpx

from app.ai.base import LLMAdapter, LLMMessage, LLMResponse
from app.core.config import settings

KIMI_TEMPERATURE = 0.6


def cost_usd(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens * settings.KIMI_PRICE_INPUT + output_tokens * settings.KIMI_PRICE_OUTPUT) / 1_000_000


class KimiAdapter(LLMAdapter):
    def __init__(self, api_key: str | None = None, default_model: str | None = None,
                 base_url: str | None = None, client: httpx.AsyncClient | None = None):
        self._api_key = api_key or settings.KIMI_API_KEY
        self._base_url = (base_url or settings.KIMI_BASE_URL).rstrip("/")
        self._default_model = default_model or settings.KIMI_MODEL
        self._client = client

    def _http(self) -> httpx.AsyncClient:
        return self._client or httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS)

    def _body(self, messages: list[LLMMessage], model: str, max_tokens: int, **extra) -> dict:
        return {"model": model, "messages": [{"role": m.role, "content": m.content} for m in messages],
                "temperature": KIMI_TEMPERATURE, "max_tokens": max_tokens * 2,
                "thinking": {"type": "disabled"}, **extra}

    async def _post(self, body: dict) -> dict:
        client = self._http()
        try:
            r = await client.post(f"{self._base_url}/chat/completions", json=body,
                                  headers={"Authorization": f"Bearer {self._api_key}"})
            r.raise_for_status()
            return r.json()
        finally:
            if self._client is None:
                await client.aclose()

    def _to_response(self, data: dict, model: str, start: float) -> LLMResponse:
        choice = (data.get("choices") or [{}])[0]
        text = ((choice.get("message") or {}).get("content") or "").strip()
        if not text:
            raise RuntimeError("Kimi devolvió una respuesta vacía")
        usage = data.get("usage") or {}
        p, c = int(usage.get("prompt_tokens") or 0), int(usage.get("completion_tokens") or 0)
        return LLMResponse(content=text, model=data.get("model") or model, prompt_tokens=p, completion_tokens=c,
                           duration_s=time.monotonic() - start, done=choice.get("finish_reason") != "length",
                           metadata={"stop_reason": choice.get("finish_reason")}, provider="kimi",
                           cost_usd=cost_usd(p, c))

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048) -> LLMResponse:
        model = model or self._default_model
        start = time.monotonic()
        return self._to_response(await self._post(self._body(messages, model, max_tokens)), model, start)

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048) -> LLMResponse:
        model = model or self._default_model
        instruction = LLMMessage("system", "Responde SOLO con un objeto JSON válido, sin texto antes ni después, "
                                           "que cumpla este esquema JSON:\n" + json.dumps(schema, ensure_ascii=False))
        start = time.monotonic()
        data = await self._post(self._body([*messages, instruction], model, max_tokens,
                                           response_format={"type": "json_object"}))
        response = self._to_response(data, model, start)
        try:
            response.parsed = json.loads(response.content)
        except json.JSONDecodeError:
            response.parsed = None
        return response

    async def chat_stream(self, messages, model=None, temperature=0.7, max_tokens=2048) -> AsyncGenerator[str, None]:
        model = model or self._default_model
        start = time.monotonic()
        body = self._body(messages, model, max_tokens, stream=True, stream_options={"include_usage": True})
        parts, usage = [], {}
        client = self._http()
        try:
            async with client.stream("POST", f"{self._base_url}/chat/completions", json=body,
                                     headers={"Authorization": f"Bearer {self._api_key}"}) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    payload = line[5:].strip()
                    if payload == "[DONE]":
                        break
                    chunk = json.loads(payload)
                    usage = chunk.get("usage") or (chunk.get("choices") or [{}])[0].get("usage") or usage
                    token = ((chunk.get("choices") or [{}])[0].get("delta") or {}).get("content")
                    if token:
                        parts.append(token)
                        yield token
        finally:
            if self._client is None:
                await client.aclose()
        self.last_stream_response = self._to_response(
            {"model": model, "choices": [{"message": {"content": "".join(parts) or " "}}], "usage": usage},
            model, start)

    async def generate(self, prompt, model=None, system=None, temperature=0.7, max_tokens=2048) -> LLMResponse:
        messages = ([LLMMessage("system", system)] if system else []) + [LLMMessage("user", prompt)]
        return await self.chat(messages, model=model, max_tokens=max_tokens)

    async def health_check(self) -> bool:
        return bool(self._api_key)

    def list_models(self) -> list[str]:
        return [self._default_model]
