"""Capa de abstraccion de modelos - BP-0001 (AD-000: Ollama es un Motor del Ecosistema,
reemplazable, nunca una dependencia fija - AD-003 "Motor (de Capacidad)").

Toda inferencia pasa por esta interfaz unica. Ningun agente llama a Ollama (ni a ninguna
API externa) directamente - eso es exactamente lo que permite, en el futuro, conmutar a
otro proveedor sin tocar el runtime de agentes (Plan Maestro SS4: "conmutable a APIs
externas en el futuro")."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class ModelCallRecord:
    """Registro de modelo+version por llamada - AD-002 regla 1.7 aplicada a inferencia."""

    provider: str
    model: str
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    duration_ms: float | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    attempt: int = 1
    error: str | None = None


@dataclass
class GenerateResult:
    text: str
    call_record: ModelCallRecord


class ModelBackend(ABC):
    """Interfaz unica que cualquier proveedor de inferencia debe implementar."""

    @abstractmethod
    def generate(self, prompt: str, *, model: str | None = None, timeout_s: float = 60.0) -> GenerateResult:
        """Genera una respuesta completa (no streaming)."""

    @abstractmethod
    def generate_stream(
        self, prompt: str, *, model: str | None = None, timeout_s: float = 60.0
    ) -> Iterator[str]:
        """Genera una respuesta como stream de fragmentos de texto."""

    @abstractmethod
    def embed(self, text: str, *, model: str | None = None, timeout_s: float = 30.0) -> list[float]:
        """Genera un embedding vectorial del texto."""

    @abstractmethod
    def generate_structured(
        self, prompt: str, *, schema_hint: str, model: str | None = None, timeout_s: float = 60.0
    ) -> GenerateResult:
        """Genera una respuesta que debe seguir un formato estructurado (JSON), con el
        esquema esperado descrito en `schema_hint`. La validacion del JSON resultante es
        responsabilidad del llamador (el Agente), no de esta capa."""
