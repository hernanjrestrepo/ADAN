"""LLM Adapter Factory — registry-based, same pattern as ollama-worker's AdapterFactory.

Adding a new provider = one entry in _ADAPTERS. Never touch factory internals.
"""
from __future__ import annotations

import os

from app.ai.base import LLMAdapter
from app.core.observability import LLMTimer

_ENV_VAR = "LLM_PROVIDER"
_DEFAULT = "ollama"

# Registry: provider name -> (module path, class name)
# Lazy imports to avoid loading unused dependencies
_ADAPTERS: dict[str, tuple[str, str]] = {
    "ollama": ("app.ai.ollama_adapter", "OllamaAdapter"),
    # "openai": ("app.ai.openai_adapter", "OpenAIAdapter"),  # future
    # "anthropic": ("app.ai.anthropic_adapter", "AnthropicAdapter"),  # future
}


class InstrumentedLLM(LLMAdapter):
    """Mide cada llamada al modelo (métrica adan_llm_call_duration_seconds, WO-093)."""

    def __init__(self, inner: LLMAdapter):
        self.inner = inner

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
        with LLMTimer("chat"):
            return await self.inner.chat(messages, model=model, temperature=temperature, max_tokens=max_tokens)

    async def chat_stream(self, messages, model=None, temperature=0.7, max_tokens=2048):
        with LLMTimer("chat_stream"):
            async for token in self.inner.chat_stream(messages, model=model, temperature=temperature,
                                                      max_tokens=max_tokens):
                yield token

    async def generate(self, prompt, model=None, system=None, temperature=0.7, max_tokens=2048):
        with LLMTimer("generate"):
            return await self.inner.generate(prompt, model=model, system=system, temperature=temperature,
                                             max_tokens=max_tokens)

    async def health_check(self) -> bool:
        return await self.inner.health_check()

    def list_models(self) -> list[str]:
        return self.inner.list_models()

    def __getattr__(self, name):
        return getattr(self.inner, name)


def get_llm_adapter() -> LLMAdapter:
    """Create the configured LLM adapter. Called once at startup."""
    provider = os.getenv(_ENV_VAR, _DEFAULT).strip().lower()

    if provider not in _ADAPTERS:
        raise RuntimeError(
            f"LLM_PROVIDER={provider!r} unknown. Available: {list(_ADAPTERS.keys())}"
        )

    module_path, class_name = _ADAPTERS[provider]
    import importlib
    module = importlib.import_module(module_path)
    adapter_class = getattr(module, class_name)
    return InstrumentedLLM(adapter_class())
