"""
DKA Engines — Motores de scraping y crawling.

Cada motor implementa la misma interfaz para ser usado como herramienta del TEF.
"""

import abc
import hashlib
from dataclasses import dataclass, field
from typing import Any

from app.core.net import public_http_client


@dataclass
class ScrapedContent:
    """Contenido extraído de una fuente web."""
    url: str
    title: str
    content: str
    content_type: str                   # html, markdown, json
    metadata: dict = field(default_factory=dict)
    quality_score: float = 0.0          # 0-1
    engine_used: str = ""
    duration_ms: int = 0
    word_count: int = 0
    language: str = "es"


class ScraperEngine(abc.ABC):
    """Interfaz abstracta para motores de scraping."""

    @abc.abstractmethod
    async def scrape(self, url: str, query: str | None = None, **kwargs) -> ScrapedContent:
        """Extrae contenido de una URL."""
        ...

    @abc.abstractmethod
    def name(self) -> str:
        """Nombre del motor."""
        ...


# ============================================================
# Crawl4AI Engine (HTTP-based)
# ============================================================

class Crawl4AIEngine(ScraperEngine):
    """
    Motor principal de crawling basado en HTTP.
    Para sitios estáticos y APIs simples.
    """

    def name(self) -> str:
        return "crawl4ai"

    async def scrape(self, url: str, query: str | None = None, **kwargs) -> ScrapedContent:
        import time
        start = time.time()

        try:
            async with public_http_client(timeout=30, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; ADAN/1.0)"
                })
                response.raise_for_status()

                content = response.text
                title = self._extract_title(content)

                # Convertir HTML básico a texto
                text = self._html_to_text(content)

                duration_ms = int((time.time() - start) * 1000)

                return ScrapedContent(
                    url=url,
                    title=title,
                    content=text[:10000],
                    content_type="text",
                    quality_score=self._assess_quality(text),
                    engine_used="crawl4ai",
                    duration_ms=duration_ms,
                    word_count=len(text.split()),
                )

        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            return ScrapedContent(
                url=url,
                title="Error",
                content=f"Error scraping {url}: {str(e)}",
                content_type="error",
                quality_score=0.0,
                engine_used="crawl4ai",
                duration_ms=duration_ms,
            )

    def _extract_title(self, html: str) -> str:
        """Extrae título del HTML."""
        import re
        match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else "Sin título"

    def _html_to_text(self, html: str) -> str:
        """Convierte HTML a texto plano básico."""
        import re
        # Remover tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        # Remover scripts y styles
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _assess_quality(self, text: str) -> float:
        """Evalúa calidad del contenido."""
        score = 0.5
        if len(text) > 500:
            score += 0.2
        if len(text) > 2000:
            score += 0.1
        if len(text.split()) > 100:
            score += 0.1
        return min(score, 1.0)


# ============================================================
# ScrapeGraphAI Engine (IA-based extraction)
# ============================================================

class ScrapeGraphAIEngine(ScraperEngine):
    """
    Motor de extracción inteligente basado en IA.
    Usa LLM para entender y extraer información estructurada.
    """

    def __init__(self, llm=None):
        self._llm = llm

    def name(self) -> str:
        return "scrapegraph"

    async def scrape(self, url: str, query: str | None = None, **kwargs) -> ScrapedContent:
        import time
        start = time.time()

        try:
            # Primero obtener el contenido raw
            crawl4ai = Crawl4AIEngine()
            raw_content = await crawl4ai.scrape(url)

            if raw_content.content_type == "error":
                return raw_content

            # Si hay LLM disponible, usar para extracción inteligente
            if self._llm and query:
                extracted = await self._extract_with_llm(raw_content.content, query)
                duration_ms = int((time.time() - start) * 1000)
                return ScrapedContent(
                    url=url,
                    title=raw_content.title,
                    content=extracted,
                    content_type="structured",
                    quality_score=min(raw_content.quality_score + 0.2, 1.0),
                    engine_used="scrapegraph",
                    duration_ms=duration_ms,
                    word_count=len(extracted.split()),
                    metadata={"query": query, "raw_length": len(raw_content.content)},
                )
            else:
                # Sin LLM, retornar contenido raw
                raw_content.engine_used = "scrapegraph"
                raw_content.duration_ms = int((time.time() - start) * 1000)
                return raw_content

        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            return ScrapedContent(
                url=url,
                title="Error",
                content=f"Error: {str(e)}",
                content_type="error",
                quality_score=0.0,
                engine_used="scrapegraph",
                duration_ms=duration_ms,
            )

    async def _extract_with_llm(self, content: str, query: str) -> str:
        """Usa LLM para extraer información relevante."""
        from app.ai.base import LLMMessage

        prompt = f"""Extrae información relevante de este contenido web.

QUERY: {query}

CONTENIDO (primeros 5000 chars):
{content[:5000]}

Retorna SOLO el texto relevante, limpio y estructurado. Sin explicaciones."""

        try:
            messages = [LLMMessage(role="user", content=prompt)]
            response = await self._llm.chat(messages, temperature=0.3, max_tokens=2000)
            return response.content
        except Exception:
            return content[:5000]


# ============================================================
# Firecrawl Engine (headless browser)
# ============================================================

class FirecrawlEngine(ScraperEngine):
    """
    Motor para sitios con JavaScript pesado.
    Usa httpx con headers de navegador para simular.
    """

    def name(self) -> str:
        return "firecrawl"

    async def scrape(self, url: str, query: str | None = None, **kwargs) -> ScrapedContent:
        import time
        start = time.time()

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            }

            async with public_http_client(timeout=30, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                content = response.text
                title = self._extract_title(content)
                text = self._html_to_text(content)

                duration_ms = int((time.time() - start) * 1000)

                return ScrapedContent(
                    url=url,
                    title=title,
                    content=text[:10000],
                    content_type="text",
                    quality_score=min(0.7 + len(text) / 10000, 1.0),
                    engine_used="firecrawl",
                    duration_ms=duration_ms,
                    word_count=len(text.split()),
                )

        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            return ScrapedContent(
                url=url,
                title="Error",
                content=f"Error: {str(e)}",
                content_type="error",
                quality_score=0.0,
                engine_used="firecrawl",
                duration_ms=duration_ms,
            )

    def _extract_title(self, html: str) -> str:
        import re
        match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else "Sin título"

    def _html_to_text(self, html: str) -> str:
        import re
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text


# ============================================================
# Engine Selector
# ============================================================

class EngineSelector:
    """
    Selecciona automáticamente el motor de scraping adecuado
    según la naturaleza de la URL y la query.
    """

    ENGINES = {
        "crawl4ai": Crawl4AIEngine,
        "scrapegraph": ScrapeGraphAIEngine,
        "firecrawl": FirecrawlEngine,
    }

    @classmethod
    def select(cls, url: str, query: str | None = None, llm=None) -> ScraperEngine:
        """Selecciona el mejor motor para la URL."""
        url_lower = url.lower()

        # Sitios con JS pesado
        js_heavy = ["react", "angular", "vue", "next", "nuxt", "spa"]
        if any(js in url_lower for js in js_heavy):
            return FirecrawlEngine()

        # Si hay query y LLM disponible, usar extracción inteligente
        if query and llm:
            return ScrapeGraphAIEngine(llm=llm)

        # Default: Crawl4AI
        return Crawl4AIEngine()
