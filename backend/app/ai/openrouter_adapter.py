"""Adaptador de OpenRouter: cientos de modelos con una sola clave, por su API compatible con OpenAI.

- El costo de cada llamada sale de `usage.cost`, que OpenRouter informa en dólares; si falta, se estima con
  el catálogo (`app/ai/catalog.py`).
- `chat_json` usa salidas estructuradas (`response_format: json_schema`) cuando el modelo las admite.
- Sin parámetros de muestreo para modelos de razonamiento: no se envía `temperature` salvo que se pida.
"""
from __future__ import annotations

import json
import time
from typing import AsyncGenerator

import httpx

from app.ai import catalog
from app.ai.base import LLMAdapter, LLMMessage, LLMResponse
from app.core.config import settings


class OpenRouterAdapter(LLMAdapter):
    def __init__(self, api_key: str | None = None, default_model: str = "anthropic/claude-haiku-5.5",
                 base_url: str | None = None, client: httpx.AsyncClient | None = None):
        self._api_key = api_key or settings.OPENROUTER_API_KEY
        self._base_url = (base_url or settings.OPENROUTER_BASE_URL).rstrip("/")
        self._default_model = default_model
        self._client = client

    def _http(self) -> httpx.AsyncClient:
        return self._client or httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS)

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._api_key}", "HTTP-Referer": settings.PUBLIC_URL, "X-Title": "ADAN"}

    @staticmethod
    def _body(messages: list[LLMMessage], model: str, max_tokens: int, **extra) -> dict:
        return {"model": model, "messages": [{"role": m.role, "content": m.content} for m in messages],
                "max_tokens": max_tokens, "usage": {"include": True}, **extra}

    async def _post(self, body: dict) -> dict:
        client = self._http()
        try:
            r = await client.post(f"{self._base_url}/chat/completions", json=body, headers=self._headers())
            r.raise_for_status()
            data = r.json()
        finally:
            if self._client is None:
                await client.aclose()
        if data.get("error"):
            raise RuntimeError(f"OpenRouter: {str(data['error'])[:200]}")
        return data

    def _to_response(self, data: dict, model: str, start: float) -> LLMResponse:
        choice = (data.get("choices") or [{}])[0]
        text = ((choice.get("message") or {}).get("content") or "").strip()
        if not text:
            raise RuntimeError("OpenRouter devolvió una respuesta vacía")
        usage = data.get("usage") or {}
        p, c = int(usage.get("prompt_tokens") or 0), int(usage.get("completion_tokens") or 0)
        cost = usage.get("cost")
        if cost is None:
            spec = next((m for m in catalog.load() if m.provider == "openrouter" and m.model == model), None)
            cost = catalog.estimate_cost(spec, p, c) if spec else 0.0
        return LLMResponse(content=text, model=data.get("model") or model, prompt_tokens=p, completion_tokens=c,
                           duration_s=time.monotonic() - start, done=choice.get("finish_reason") != "length",
                           metadata={"stop_reason": choice.get("finish_reason")}, provider="openrouter",
                           cost_usd=float(cost))

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048) -> LLMResponse:
        model = model or self._default_model
        start = time.monotonic()
        return self._to_response(await self._post(self._body(messages, model, max_tokens)), model, start)

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048) -> LLMResponse:
        model = model or self._default_model
        start = time.monotonic()
        # Los modelos con razonamiento gastan parte del tope pensando: sin margen el JSON sale cortado
        body = self._body(messages, model, max(max_tokens * 3, 4000), response_format={
            "type": "json_schema", "json_schema": {"name": "respuesta", "strict": True, "schema": schema}})
        response = self._to_response(await self._post(body), model, start)
        try:
            response.parsed = json.loads(response.content)
        except json.JSONDecodeError:
            response.parsed = None
        return response

    async def chat_stream(self, messages, model=None, temperature=0.7, max_tokens=2048) -> AsyncGenerator[str, None]:
        model = model or self._default_model
        start = time.monotonic()
        body = self._body(messages, model, max_tokens, stream=True)
        parts, usage = [], {}
        client = self._http()
        try:
            async with client.stream("POST", f"{self._base_url}/chat/completions", json=body,
                                     headers=self._headers()) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    payload = line[5:].strip()
                    if payload == "[DONE]":
                        break
                    chunk = json.loads(payload)
                    usage = chunk.get("usage") or usage
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
