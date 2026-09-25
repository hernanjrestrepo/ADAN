"""Ollama adapter — concrete implementation for local Qwen models."""
from __future__ import annotations

import json
import time
from typing import AsyncGenerator

import httpx

from app.ai.base import LLMAdapter, LLMMessage, LLMResponse, extract_json
from app.core.config import settings


class OllamaAdapter(LLMAdapter):
    """Ollama-backed LLM adapter. Default for local development."""

    def __init__(self, base_url: str | None = None, default_model: str | None = None):
        self._base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self._default_model = default_model or settings.DEFAULT_MODEL

    async def chat(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        json_schema: dict | None = None,
    ) -> LLMResponse:
        model = model or self._default_model
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if json_schema is not None:
            payload["format"] = json_schema  # Ollama restringe la salida al esquema
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
            resp = await client.post(f"{self._base_url}/api/chat", json=payload)
            resp.raise_for_status()
        data = resp.json()
        duration = time.monotonic() - start

        message = data.get("message", {})
        return LLMResponse(
            content=message.get("content", ""),
            model=model,
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            duration_s=duration,
            done=data.get("done", True),
            metadata={"eval_duration_ns": data.get("eval_duration", 0)},
            provider="ollama",
        )

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048) -> LLMResponse:
        response = await self.chat(messages, model=model, temperature=temperature, max_tokens=max_tokens,
                                   json_schema=schema)
        response.parsed = extract_json(response.content)
        return response

    async def chat_stream(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """Stream chat response token by token."""
        model = model or self._default_model
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
            async with client.stream("POST", f"{self._base_url}/api/chat", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "message" in data:
                                content = data["message"].get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            pass

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        model = model or self._default_model
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
            resp = await client.post(f"{self._base_url}/api/generate", json=payload)
            resp.raise_for_status()
        data = resp.json()
        duration = time.monotonic() - start

        return LLMResponse(
            content=data.get("response", ""),
            model=model,
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            duration_s=duration,
            done=data.get("done", True),
            metadata={"eval_duration_ns": data.get("eval_duration", 0)},
        )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self._base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """Synchronous list — called at startup, not per-request."""
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.get(f"{self._base_url}/api/tags")
                resp.raise_for_status()
                models = resp.json().get("models", [])
                return [m.get("name", "") for m in models]
        except Exception:
            return []
