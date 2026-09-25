"""Enrutador de modelos (WO-099, AD-DEC-0002 decisión 3).

Cada tarea declara su complejidad y el enrutador elige el modelo:

| Nivel      | Para qué                                        | Modelo por defecto             |
|------------|-------------------------------------------------|--------------------------------|
| `simple`   | Resúmenes, clasificación, planes internos       | Ollama (`DEFAULT_MODEL`)       |
| `fast`     | Respuestas cortas donde importa la latencia     | Claude Haiku (`LLM_MODEL_FAST`) |
| `standard` | Conversación con el cliente, diagnóstico        | Claude Sonnet (`LLM_MODEL_STANDARD`) |
| `complex`  | Votos del Board, decisiones y Gate Review       | Claude Opus (`LLM_MODEL_COMPLEX`) |

Sin `ANTHROPIC_API_KEY`, o si Claude falla, la llamada cae a Ollama y la respuesta queda
marcada como degradada (`metadata["degraded"]`): el servicio sigue, con menor calidad.
"""
from __future__ import annotations

import logging

from app.ai.base import LLMAdapter, LLMResponse
from app.ai.usage import record_usage
from app.core.config import settings

logger = logging.getLogger(__name__)

TIERS = ("simple", "fast", "standard", "complex")
# Esfuerzo de razonamiento por nivel (Claude)
EFFORT = {"fast": None, "standard": "low", "complex": "medium"}


def tier_model(tier: str) -> str:
    return {"fast": settings.LLM_MODEL_FAST, "standard": settings.LLM_MODEL_STANDARD,
            "complex": settings.LLM_MODEL_COMPLEX}.get(tier, settings.DEFAULT_MODEL)


class TieredLLM(LLMAdapter):
    """Vista del enrutador fija en un nivel: se usa como cualquier LLMAdapter."""

    def __init__(self, local: LLMAdapter, claude_factory, tier: str):
        if tier not in TIERS:
            raise ValueError(f"Nivel de complejidad desconocido: {tier}")
        self.local = local
        self.tier = tier
        self.claude = claude_factory(tier) if tier != "simple" else None

    async def _route(self, operation: str, call):
        if self.claude is not None:
            try:
                response = await call(self.claude, tier_model(self.tier))
                record_usage(response, self.tier, operation)
                return response
            except Exception as exc:  # red, API o rechazo: se degrada a Ollama
                logger.warning("Claude no disponible para %s (%s): se usa Ollama", operation, type(exc).__name__)
                response = await call(self.local, None)
                response.metadata["degraded"] = f"Claude no disponible ({type(exc).__name__})"
                record_usage(response, self.tier, operation)
                return response
        response = await call(self.local, None)
        if self.tier != "simple":
            response.metadata["degraded"] = "sin ANTHROPIC_API_KEY"
        record_usage(response, self.tier, operation)
        return response

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048) -> LLMResponse:
        return await self._route("chat", lambda llm, m: llm.chat(messages, model=model or m, temperature=temperature,
                                                                  max_tokens=max_tokens))

    async def chat_json(self, messages, schema, model=None, temperature=0.3, max_tokens=2048) -> LLMResponse:
        return await self._route("chat_json", lambda llm, m: llm.chat_json(
            messages, schema, model=model or m, temperature=temperature, max_tokens=max_tokens))

    async def generate(self, prompt, model=None, system=None, temperature=0.7, max_tokens=2048) -> LLMResponse:
        return await self._route("generate", lambda llm, m: llm.generate(
            prompt, model=model or m, system=system, temperature=temperature, max_tokens=max_tokens))

    async def chat_stream(self, messages, model=None, temperature=0.7, max_tokens=2048):
        llm = self.claude or self.local
        started = False
        try:
            async for token in llm.chat_stream(messages, model=model or (tier_model(self.tier) if self.claude else None),
                                               temperature=temperature, max_tokens=max_tokens):
                started = True
                yield token
        except Exception as exc:
            if self.claude is None or started:
                raise
            logger.warning("Claude no disponible para chat_stream (%s): se usa Ollama", type(exc).__name__)
            async for token in self.local.chat_stream(messages, model=model, temperature=temperature,
                                                      max_tokens=max_tokens):
                yield token
            return
        final = getattr(llm, "last_stream_response", None)
        if final is not None:
            record_usage(final, self.tier, "chat_stream")

    async def health_check(self) -> bool:
        return await self.local.health_check()

    def list_models(self) -> list[str]:
        return self.local.list_models()


class ModelRouter(TieredLLM):
    """El enrutador: sin nivel explícito usa `simple` (Ollama); `for_tier` da las demás vistas."""

    def __init__(self, local: LLMAdapter, claude_factory=None):
        self._claude_factory = claude_factory or _default_claude_factory()
        super().__init__(local, self._claude_factory, "simple")

    def for_tier(self, tier: str) -> TieredLLM:
        return TieredLLM(self.local, self._claude_factory, tier)


def _default_claude_factory():
    if not settings.ANTHROPIC_API_KEY:
        return lambda tier: None

    from app.ai.anthropic_adapter import AnthropicAdapter

    def factory(tier: str):
        return AnthropicAdapter(default_model=tier_model(tier), effort=EFFORT.get(tier))
    return factory


def for_tier(llm: LLMAdapter, tier: str) -> LLMAdapter:
    """La vista de un nivel si el adaptador es un enrutador; si no (p. ej. un mock de prueba), el mismo."""
    view = getattr(type(llm), "for_tier", None)
    return view(llm, tier) if view is not None else llm
