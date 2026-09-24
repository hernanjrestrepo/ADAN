"""
DKA Pipeline — Pipeline completo de adquisición de conocimiento.

Internet → Crawler → Extractor → Normalizer → Quality Score → EMS → Knowledge Graph
"""

import uuid
import hashlib
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field

from app.dka.engines import ScraperEngine, ScrapedContent, EngineSelector
from app.ems.memory import EnterpriseMemorySystem


@dataclass
class AcquisitionResult:
    """Resultado de la adquisición de conocimiento."""
    query: str = ""
    sources_scraped: int = 0
    sources_succeeded: int = 0
    sources_failed: int = 0
    chunks_created: int = 0
    quality_scores: list[float] = field(default_factory=list)
    avg_quality: float = 0.0
    engine_used: str = ""
    total_duration_ms: int = 0
    documents: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class KnowledgeAcquisitionPipeline:
    """
    Pipeline completo de adquisición de conocimiento.
    
    Flujo:
    1. Recibir query
    2. Buscar URLs relevantes (simulado por ahora)
    3. Seleccionar motor de scraping
    4. Scrappear cada URL
    5. Normalizar contenido
    6. Evaluar calidad
    7. Almacenar en EMS
    8. Retornar resultado
    """

    def __init__(
        self,
        ems: EnterpriseMemorySystem,
        llm=None,
    ):
        self.ems = ems
        self.llm = llm

    async def acquire(
        self,
        query: str,
        company_id: str,
        urls: list[str] | None = None,
        max_sources: int = 5,
    ) -> AcquisitionResult:
        """
        Ejecuta el pipeline completo de adquisición.
        """
        start_time = time.time()
        result = AcquisitionResult(query=query, sources_scraped=0)

        # 1. Obtener URLs (si no se proporcionan, buscar)
        if not urls:
            urls = await self._discover_urls(query)
        
        urls = urls[:max_sources]
        result.sources_scraped = len(urls)

        # 2. Scrappear cada URL
        for url in urls:
            try:
                # Seleccionar motor
                engine = EngineSelector.select(url, query, self.llm)
                result.engine_used = engine.name()

                # Scrappear
                content = await engine.scrape(url, query)

                if content.content_type == "error":
                    result.errors.append(f"{url}: {content.content}")
                    result.sources_failed += 1
                    continue

                # 3. Normalizar
                normalized = self._normalize_content(content)

                # 4. Evaluar calidad
                quality = self._assess_quality(normalized)
                result.quality_scores.append(quality)

                # 5. Almacenar en EMS (solo si calidad > 0.3)
                if quality > 0.3:
                    ingest_result = await self.ems.ingest(
                        company_id=company_id,
                        text=normalized.content,
                        title=normalized.title,
                        source_type="web_scrape",
                        source_name=url,
                        metadata={
                            "url": url,
                            "engine": engine.name(),
                            "quality_score": quality,
                            "word_count": normalized.word_count,
                            "acquired_at": datetime.now(timezone.utc).isoformat(),
                        },
                    )

                    result.chunks_created += ingest_result.chunks_created
                    result.documents.append({
                        "url": url,
                        "title": normalized.title,
                        "quality": quality,
                        "chunks": ingest_result.chunks_created,
                    })
                    result.sources_succeeded += 1
                else:
                    result.errors.append(f"{url}: Calidad insuficiente ({quality:.2f})")
                    result.sources_failed += 1

            except Exception as e:
                result.errors.append(f"{url}: {str(e)}")
                result.sources_failed += 1

        # Calcular métricas
        if result.quality_scores:
            result.avg_quality = sum(result.quality_scores) / len(result.quality_scores)
        
        result.total_duration_ms = int((time.time() - start_time) * 1000)

        return result

    async def _discover_urls(self, query: str) -> list[str]:
        """
        Descubre URLs relevantes para una query.
        Por ahora usa URLs hardcodeadas de demostración.
        En producción, esto conectaría a un motor de búsqueda.
        """
        # URLs de demostración para testing
        demo_urls = {
            "bpo colombia": [
                "https://www.procolombia.co/inversión/sectores/servicios",
                "https://www.banrep.gov.co/es/estadisticas",
            ],
            "mercado colombiano": [
                "https://www.dane.gov.co/",
                "https://www.banrep.gov.co/es/estadisticas",
            ],
            "default": [
                "https://httpbin.org/html",
                "https://httpbin.org/json",
            ],
        }

        query_lower = query.lower()
        for key, urls in demo_urls.items():
            if key in query_lower:
                return urls

        return demo_urls["default"]

    def _normalize_content(self, content: ScrapedContent) -> ScrapedContent:
        """Normaliza el contenido extraído."""
        # Limpiar texto
        text = content.content
        text = text.strip()

        # Remover caracteres especiales
        text = text.encode('utf-8', errors='ignore').decode('utf-8')

        # Limitar tamaño
        if len(text) > 15000:
            text = text[:15000]

        content.content = text
        content.word_count = len(text.split())

        return content

    def _assess_quality(self, content: ScrapedContent) -> float:
        """Evalúa la calidad del contenido extraído."""
        score = 0.3  # Base

        # Factor de longitud
        if content.word_count > 100:
            score += 0.2
        if content.word_count > 500:
            score += 0.1
        if content.word_count > 1000:
            score += 0.1

        # Factor de título
        if content.title and content.title != "Sin título" and len(content.title) > 5:
            score += 0.1

        # Factor de tipo de contenido
        if content.content_type in ["text", "structured", "markdown"]:
            score += 0.1

        # Factor de engine
        if content.engine_used in ["scrapegraph", "firecrawl"]:
            score += 0.05

        return min(score, 1.0)
