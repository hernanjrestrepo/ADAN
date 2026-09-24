"""
DKA Tools — Herramientas del Tool Execution Framework para scraping.
"""

import uuid
import time
from typing import Any

from app.tef.interfaces import ToolProvider, ToolMetadata, ToolContext, ToolResult
from app.dka.engines import EngineSelector


class Crawl4AITool(ToolProvider):
    """Herramienta de crawling con Crawl4AI."""

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            id="crawl4ai",
            name="Crawl4AI",
            description="Crawlea y extrae contenido de páginas web (motor HTTP)",
            category="scraping",
            permissions=["read:web"],
            inputs={
                "url": {"type": "string", "description": "URL a crawlear", "required": True},
                "query": {"type": "string", "description": "Query para extraer información específica", "required": False},
            },
            outputs={
                "title": {"type": "string", "description": "Título de la página"},
                "content": {"type": "string", "description": "Contenido extraído"},
                "word_count": {"type": "integer", "description": "Número de palabras"},
            },
            timeout_seconds=30,
            tags=["web", "crawl", "scrape", "internet", "crawl4ai"],
        )

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        engine = EngineSelector.select(params["url"])
        result = await engine.scrape(params["url"], params.get("query"))

        return ToolResult(
            tool_id="crawl4ai",
            status="success" if result.content_type != "error" else "error",
            output={
                "title": result.title,
                "content": result.content[:5000],
                "word_count": result.word_count,
                "url": result.url,
                "engine": result.engine_used,
            },
            duration_ms=result.duration_ms,
        )


class ScrapeGraphTool(ToolProvider):
    """Herramienta de extracción inteligente con ScrapeGraphAI."""

    def __init__(self, llm=None):
        self._llm = llm

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            id="scrapegraph",
            name="ScrapeGraphAI",
            description="Extrae información estructurada de páginas web usando IA",
            category="scraping",
            permissions=["read:web"],
            inputs={
                "url": {"type": "string", "description": "URL a analizar", "required": True},
                "query": {"type": "string", "description": "Qué información extraer (en lenguaje natural)", "required": True},
            },
            outputs={
                "extracted_content": {"type": "string", "description": "Contenido extraído y estructurado"},
                "title": {"type": "string", "description": "Título de la fuente"},
            },
            timeout_seconds=60,
            tags=["web", "scrape", "ia", "extract", "structured", "scrapegraph"],
        )

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        from app.dka.engines import ScrapeGraphAIEngine
        engine = ScrapeGraphAIEngine(llm=self._llm)
        result = await engine.scrape(params["url"], params.get("query"))

        return ToolResult(
            tool_id="scrapegraph",
            status="success" if result.content_type != "error" else "error",
            output={
                "extracted_content": result.content[:5000],
                "title": result.title,
                "url": result.url,
                "quality_score": result.quality_score,
            },
            duration_ms=result.duration_ms,
        )


class FirecrawlTool(ToolProvider):
    """Herramienta de crawling avanzado con Firecrawl."""

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            id="firecrawl",
            name="Firecrawl",
            description="Crawlea sitios con JavaScript pesado",
            category="scraping",
            permissions=["read:web"],
            inputs={
                "url": {"type": "string", "description": "URL a crawlear", "required": True},
            },
            outputs={
                "title": {"type": "string", "description": "Título de la página"},
                "content": {"type": "string", "description": "Contenido extraído"},
            },
            timeout_seconds=45,
            tags=["web", "crawl", "javascript", "browser", "firecrawl"],
        )

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        from app.dka.engines import FirecrawlEngine
        engine = FirecrawlEngine()
        result = await engine.scrape(params["url"])

        return ToolResult(
            tool_id="firecrawl",
            status="success" if result.content_type != "error" else "error",
            output={
                "title": result.title,
                "content": result.content[:5000],
                "word_count": result.word_count,
            },
            duration_ms=result.duration_ms,
        )
