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

    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_models(self) -> list[str]:
        raise NotImplementedError
