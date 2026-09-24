"""LLM Adapter Factory — registry-based, same pattern as ollama-worker's AdapterFactory.

Adding a new provider = one entry in _ADAPTERS. Never touch factory internals.
"""
from __future__ import annotations

import os

from app.ai.base import LLMAdapter

_ENV_VAR = "LLM_PROVIDER"
_DEFAULT = "ollama"

# Registry: provider name -> (module path, class name)
# Lazy imports to avoid loading unused dependencies
_ADAPTERS: dict[str, tuple[str, str]] = {
    "ollama": ("app.ai.ollama_adapter", "OllamaAdapter"),
    # "openai": ("app.ai.openai_adapter", "OpenAIAdapter"),  # future
    # "anthropic": ("app.ai.anthropic_adapter", "AnthropicAdapter"),  # future
}


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
    return adapter_class()
