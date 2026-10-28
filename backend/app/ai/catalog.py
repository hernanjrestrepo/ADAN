"""Catálogo de modelos y selección por costo-beneficio (modo inteligente, WO-099).

Cada tarea pide una calidad mínima y unas capacidades; el selector elige, entre los proveedores que tienen
clave, el modelo MÁS BARATO que las cumple. Así lo simple no paga un modelo caro y lo importante (votos del
Board, código del MVP) no se hace con uno que no da la talla.

- `quality` (1 a 5) es un nivel ASIGNADO por Paradixe según el uso que se le dará, no una medición. Hay que
  validarlo con evaluaciones (ver `docs/economia/COSTOS_Y_MARGEN.md`) antes de bajar la calidad exigida.
- Precios: de lista, en USD por millón de tokens (`catalog.json`, con fecha). `scripts/refresh_catalog.py` los
  vuelve a leer de OpenRouter. Imagen: precio por token de imagen y un número de tokens por imagen aproximado.
- Video: OpenRouter no lista modelos de generación de video; el catálogo ya admite la modalidad `video`
  (precio por segundo) para agregarlos cuando haya un proveedor, pero hoy no hay ninguno.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from app.core.config import settings

PROVIDER_RANK = {"anthropic": 0, "kimi": 1, "openrouter": 2, "ollama": 3}   # a igual costo y calidad, el directo
MODALITIES = ("text", "image", "video")


@dataclass(frozen=True)
class ModelSpec:
    id: str
    provider: str
    model: str
    modality: str
    quality: int
    input_per_m: float = 0.0
    output_per_m: float = 0.0
    image_output_per_m: float = 0.0     # imagen: USD por millón de tokens de imagen
    per_second_usd: float = 0.0         # video: USD por segundo
    vision: bool = False
    tools: bool = False
    json: bool = False
    context: int = 0
    note: str = ""


@dataclass(frozen=True)
class Task:
    """Lo que pide una tarea: calidad mínima, capacidades y tamaño típico (para estimar el costo)."""
    min_quality: int
    modality: str = "text"
    needs: tuple[str, ...] = ()
    input_tokens: int = 3000
    output_tokens: int = 600
    why: str = ""


TASKS: dict[str, Task] = {
    "clasificar":   Task(2, needs=("json",), input_tokens=800, output_tokens=150, why="etiquetar, extraer campos"),
    "resumir":      Task(2, input_tokens=4000, output_tokens=500, why="resúmenes de conversaciones"),
    "rapida":       Task(2, input_tokens=2000, output_tokens=300, why="respuestas cortas donde manda la latencia"),
    "conversacion": Task(3, input_tokens=4000, output_tokens=500, why="el chat con el cliente"),
    "documento":    Task(3, input_tokens=6000, output_tokens=3000, why="entregables, diagnóstico, informes"),
    "decision":     Task(4, needs=("json",), input_tokens=5000, output_tokens=900,
                         why="votos del Board, Gate Review: decisiones que paga el cliente"),
    "codigo_mvp":   Task(4, needs=("tools",), input_tokens=60_000, output_tokens=12_000,
                         why="programar el MVP: un error cuesta más que el modelo"),
    "vision":       Task(3, needs=("vision",), input_tokens=3000, output_tokens=500, why="OCR, capturas, planos"),
    "imagen":       Task(2, modality="image", why="logos, mockups, material gráfico"),
    "imagen_final": Task(4, modality="image", why="piezas que el cliente publica"),
    "video":        Task(3, modality="video", why="clips y animaciones (sin proveedor todavía)"),
}
# El enrutador por niveles (simple/fast/standard/complex) se apoya en estas tareas
TIER_TASK = {"fast": "rapida", "standard": "conversacion", "complex": "decision"}


@dataclass
class Choice:
    spec: ModelSpec
    est_cost_usd: float
    alternatives: list[tuple[ModelSpec, float]] = field(default_factory=list)


@lru_cache(maxsize=1)
def _raw() -> dict:
    return json.loads((Path(__file__).with_name("catalog.json")).read_text())


@lru_cache(maxsize=1)
def load() -> tuple[ModelSpec, ...]:
    out = []
    for m in _raw()["models"]:
        spec = ModelSpec(**{k: m[k] for k in ModelSpec.__dataclass_fields__ if k in m})
        if spec.provider == "kimi":   # el precio de Kimi directo se configura
            spec = ModelSpec(**{**spec.__dict__, "input_per_m": settings.KIMI_PRICE_INPUT,
                                "output_per_m": settings.KIMI_PRICE_OUTPUT})
        out.append(spec)
    return tuple(out)


def available_providers() -> set[str]:
    """Los proveedores que tienen clave; Ollama siempre (es local)."""
    keys = {"anthropic": settings.ANTHROPIC_API_KEY, "kimi": settings.KIMI_API_KEY,
            "openrouter": settings.OPENROUTER_API_KEY}
    return {"ollama"} | {p for p, key in keys.items() if key}


def estimate_cost(spec: ModelSpec, input_tokens: int = 0, output_tokens: int = 0, images: int = 0,
                  seconds: float = 0.0) -> float:
    if spec.modality == "image":
        per_image = spec.image_output_per_m * _raw().get("image_tokens_per_image", 1290) / 1_000_000
        return images * per_image + (input_tokens * spec.input_per_m + output_tokens * spec.output_per_m) / 1_000_000
    if spec.modality == "video":
        return seconds * spec.per_second_usd
    return (input_tokens * spec.input_per_m + output_tokens * spec.output_per_m) / 1_000_000


def _fits(spec: ModelSpec, task: Task, min_quality: int) -> bool:
    return (spec.modality == task.modality and spec.quality >= min_quality
            and all(getattr(spec, need) for need in task.needs))


def select(task: str | Task, *, providers: set[str] | None = None, min_quality: int | None = None,
           exclude: tuple[str, ...] = (), images: int = 1, seconds: float = 5.0) -> Choice:
    """El modelo más barato que cumple la tarea entre los proveedores disponibles.

    Orden: costo estimado, luego mayor calidad, luego proveedor directo antes que intermediario. Levanta
    `LookupError` si ninguno cumple (no se baja la calidad en silencio).
    """
    spec_task = TASKS[task] if isinstance(task, str) else task
    floor = spec_task.min_quality if min_quality is None else min_quality
    allowed = available_providers() if providers is None else providers
    scored = sorted(
        ((m, estimate_cost(m, spec_task.input_tokens, spec_task.output_tokens, images, seconds))
         for m in load() if m.provider in allowed and m.id not in exclude and _fits(m, spec_task, floor)),
        key=lambda pair: (pair[1], -pair[0].quality, PROVIDER_RANK.get(pair[0].provider, 9)))
    if not scored:
        raise LookupError(f"Ningún modelo disponible cumple «{task}» (calidad ≥ {floor}, modalidad "
                          f"{spec_task.modality}, proveedores {sorted(allowed)})")
    return Choice(spec=scored[0][0], est_cost_usd=scored[0][1], alternatives=scored[1:4])


def for_tier(tier: str, **kwargs) -> Choice:
    return select(TIER_TASK[tier], **kwargs)
