"""
Tool Manager — Gestión básica de herramientas.

Registra herramientas disponibles, sugiere cuáles usar,
y ejecuta con timeout y fallback.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable


@dataclass
class ToolDef:
    """Definición de una herramienta."""
    id: str
    name: str
    description: str
    category: str
    tags: list[str]
    handler: Callable[..., Awaitable[Any]]
    timeout_seconds: int = 30
    required_permissions: list[str] = field(default_factory=list)


@dataclass
class ToolResult:
    """Resultado de ejecución de una herramienta."""
    tool_id: str
    status: str  # "success", "failed", "timeout"
    output: Any = None
    duration_ms: int = 0
    error: str | None = None


class ToolManager:
    """
    Gestor básico de herramientas para el vertical slice.
    """

    def __init__(self):
        self._tools: dict[str, ToolDef] = {}

    def register(self, tool: ToolDef):
        """Registra una herramienta."""
        self._tools[tool.id] = tool

    def get(self, tool_id: str) -> ToolDef | None:
        """Obtiene una herramienta por ID."""
        return self._tools.get(tool_id)

    def list_all(self) -> list[ToolDef]:
        """Lista todas las herramientas registradas."""
        return list(self._tools.values())

    def discover(self, need_description: str, top_k: int = 3) -> list[ToolDef]:
        """Sugiere herramientas basándose en la necesidad descrita."""
        need_lower = need_description.lower()
        scored = []

        for tool in self._tools.values():
            score = 0.0
            # Score por match de tags
            for tag in tool.tags:
                if tag.lower() in need_lower:
                    score += 0.5
            # Score por match de nombre
            if any(w in need_lower for w in tool.name.lower().split()):
                score += 0.3
            # Score por match de descripción
            desc_words = tool.description.lower().split()
            for word in desc_words:
                if word in need_lower and len(word) > 3:
                    score += 0.2

            if score > 0:
                scored.append((tool, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, _ in scored[:top_k]]

    async def execute(self, tool_id: str, **kwargs) -> ToolResult:
        """Ejecuta una herramienta con timeout."""
        tool = self._tools.get(tool_id)
        if not tool:
            return ToolResult(
                tool_id=tool_id,
                status="failed",
                error=f"Herramienta '{tool_id}' no encontrada",
            )

        start = time.time()
        try:
            output = await tool.handler(**kwargs)
            duration_ms = int((time.time() - start) * 1000)
            return ToolResult(
                tool_id=tool_id,
                status="success",
                output=output,
                duration_ms=duration_ms,
            )
        except TimeoutError:
            duration_ms = int((time.time() - start) * 1000)
            return ToolResult(
                tool_id=tool_id,
                status="timeout",
                duration_ms=duration_ms,
                error=f"Timeout después de {tool.timeout_seconds}s",
            )
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            return ToolResult(
                tool_id=tool_id,
                status="failed",
                duration_ms=duration_ms,
                error=str(e),
            )
