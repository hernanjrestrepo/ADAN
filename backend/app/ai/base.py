"""LLM Adapter — abstract base for model providers.

Pattern inherited from ollama-worker's TransportAdapter.
Change model = change adapter. Never couple to a provider.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    duration_s: float = 0.0
    done: bool = True
    metadata: dict = field(default_factory=dict)
    provider: str = ""
    cost_usd: float = 0.0
    parsed: dict | None = None  # salida estructurada validada (chat_json)


@dataclass
class LLMMessage:
    role: str  # "system", "user", "assistant"
    content: str


class LLMAdapter(ABC):
    """Base adapter — every provider implements this."""

    @abstractmethod
    async def chat(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        raise NotImplementedError

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        raise NotImplementedError

    async def chat_json(
        self,
        messages: list[LLMMessage],
        schema: dict,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Respuesta que cumple un esquema JSON. Por defecto: chat + extracción del JSON.

        Los adaptadores que soportan salidas estructuradas (Ollama `format`, Anthropic
        `output_config.format`) la sobrescriben para que el modelo quede restringido al esquema.
        """
        response = await self.chat(messages, model=model, temperature=temperature, max_tokens=max_tokens)
        response.parsed = extract_json(response.content)
        return response

    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_models(self) -> list[str]:
        raise NotImplementedError


def extract_json(content: str) -> dict | None:
    """El primer objeto JSON de un texto (admite bloques ```json)."""
    import json

    text = (content or "").strip()
    if "```" in text:
        parts = text.split("```")
        text = parts[1].removeprefix("json").strip() if len(parts) > 1 else text
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None
