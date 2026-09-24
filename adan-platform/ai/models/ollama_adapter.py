"""Adaptador Ollama - la unica parte del sistema que sabe que existe Ollama.
Ver ADR-001 (backend/../docs/adr) - Ollama del host, nunca contenerizado."""

import json
import logging
import time
from collections.abc import Iterator

import httpx

from config import get_ai_settings
from models.base import GenerateResult, ModelBackend, ModelCallRecord

logger = logging.getLogger("adan.ai.ollama")


class OllamaBackend(ModelBackend):
    def __init__(self, base_url: str | None = None, max_retries: int = 3):
        settings = get_ai_settings()
        self.base_url = base_url or settings.ollama_base_url
        self.default_model = settings.default_model
        self.max_retries = max_retries

    def _call_with_retries(self, fn, *args, **kwargs):
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return fn(*args, **kwargs), attempt, None
            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                last_exc = exc
                logger.warning("Ollama call failed (attempt %d/%d): %s", attempt, self.max_retries, exc)
                if attempt < self.max_retries:
                    time.sleep(0.5 * attempt)  # backoff simple
        raise last_exc  # noqa: RSE102 - se propaga tras agotar reintentos

    def generate(self, prompt: str, *, model: str | None = None, timeout_s: float = 60.0) -> GenerateResult:
        model = model or self.default_model
        record = ModelCallRecord(provider="ollama", model=model)

        def _do():
            resp = httpx.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=timeout_s,
            )
            resp.raise_for_status()
            return resp.json()

        try:
            body, attempt, _ = self._call_with_retries(_do)
        except Exception as exc:  # noqa: BLE001
            record.error = str(exc)
            record.finished_at = record.started_at
            raise
        record.attempt = attempt
        record.finished_at = None
        record.prompt_tokens = body.get("prompt_eval_count")
        record.completion_tokens = body.get("eval_count")
        return GenerateResult(text=body.get("response", ""), call_record=record)

    def generate_stream(
        self, prompt: str, *, model: str | None = None, timeout_s: float = 60.0
    ) -> Iterator[str]:
        model = model or self.default_model
        with httpx.stream(
            "POST",
            f"{self.base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": True},
            timeout=timeout_s,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                if chunk.get("response"):
                    yield chunk["response"]
                if chunk.get("done"):
                    break

    def embed(self, text: str, *, model: str | None = None, timeout_s: float = 30.0) -> list[float]:
        model = model or "nomic-embed-text"

        def _do():
            resp = httpx.post(
                f"{self.base_url}/api/embed",
                json={"model": model, "input": text},
                timeout=timeout_s,
            )
            resp.raise_for_status()
            return resp.json()

        body, _, _ = self._call_with_retries(_do)
        embeddings = body.get("embeddings", [[]])
        return embeddings[0] if embeddings else []

    def generate_structured(
        self, prompt: str, *, schema_hint: str, model: str | None = None, timeout_s: float = 60.0
    ) -> GenerateResult:
        structured_prompt = (
            f"{prompt}\n\nResponde UNICAMENTE con un JSON valido que siga esta forma, "
            f"sin texto adicional antes o despues:\n{schema_hint}"
        )
        return self.generate(structured_prompt, model=model, timeout_s=timeout_s)
