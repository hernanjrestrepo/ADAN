"""
Tool Registry — Registro dinámico de herramientas.
"""

from app.tef.interfaces import ToolProvider, ToolMetadata, ToolRegistryInterface


class ToolRegistry(ToolRegistryInterface):
    """
    Registro dinámico de herramientas.
    
    Permite:
    - Registrar herramientas dinámicamente
    - Descubrir herramientas por query
    - Filtrar por permisos
    - Obtener por ID
    """

    def __init__(self):
        self._tools: dict[str, ToolProvider] = {}

    def register(self, tool: ToolProvider) -> None:
        """Registra una herramienta."""
        meta = tool.metadata()
        self._tools[meta.id] = tool

    def get(self, tool_id: str) -> ToolProvider | None:
        """Obtiene una herramienta por ID."""
        return self._tools.get(tool_id)

    def list_all(self) -> list[ToolMetadata]:
        """Lista todas las herramientas registradas."""
        return [tool.metadata() for tool in self._tools.values()]

    def discover(
        self,
        query: str,
        permissions: list[str] | None = None,
    ) -> list[ToolMetadata]:
        """
        Descubre herramientas relevantes para una query.
        
        Score por:
        - Match de tags (0.4)
        - Match de nombre/descripción (0.4)
        - Bonus por permisos (0.2)
        """
        query_lower = query.lower()
        scored = []

        for tool in self._tools.values():
            meta = tool.metadata()
            score = 0.0

            # Score por tags
            for tag in meta.tags:
                if tag.lower() in query_lower:
                    score += 0.4

            # Score por nombre/descripción
            name_words = meta.name.lower().split()
            desc_words = meta.description.lower().split()
            for word in name_words + desc_words:
                if len(word) > 3 and word in query_lower:
                    score += 0.2

            # Bonus por permisos
            if permissions:
                has_perms = all(p in permissions for p in meta.permissions)
                if has_perms:
                    score += 0.2

            if score > 0:
                scored.append((meta, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [meta for meta, _ in scored]

    def list_by_category(self, category: str) -> list[ToolMetadata]:
        """Lista herramientas por categoría."""
        return [
            tool.metadata()
            for tool in self._tools.values()
            if tool.metadata().category == category
        ]

    def count(self) -> int:
        """Retorna la cantidad de herramientas registradas."""
        return len(self._tools)
