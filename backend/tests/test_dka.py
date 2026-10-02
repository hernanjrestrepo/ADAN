"""
Tests para Dynamic Knowledge Acquisition — WO-009.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.models import User, Company
from app.dka.engines import (
    Crawl4AIEngine, ScrapeGraphAIEngine, FirecrawlEngine,
    EngineSelector, ScrapedContent,
)
from app.dka.pipeline import KnowledgeAcquisitionPipeline
from app.ems.memory import EnterpriseMemorySystem
from app.ems.providers import LocalEmbeddingProvider, LocalVectorStoreProvider


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def embedding_provider():
    return LocalEmbeddingProvider(dim=64)


@pytest.fixture
def vector_store():
    return LocalVectorStoreProvider()


@pytest.fixture
def ems(db_session, embedding_provider, vector_store):
    return EnterpriseMemorySystem(db_session, embedding_provider, vector_store)


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.chat = AsyncMock(return_value=MagicMock(
        content="Información extraída de la página: empresa de tecnología SaaS con 50 clientes",
        model="test",
        prompt_tokens=50,
        completion_tokens=30,
        duration_s=0.1,
    ))
    return llm


# ============================================================
# Tests: Engines
# ============================================================

class TestCrawl4AIEngine:
    @pytest.mark.asyncio
    async def test_scrape_local_page(self, local_site):
        engine = Crawl4AIEngine()
        result = await engine.scrape(f"{local_site}/html")
        assert result.content_type == "text"
        assert result.word_count > 0
        assert result.engine_used == "crawl4ai"

    @pytest.mark.asyncio
    async def test_scrape_invalid_url(self):
        engine = Crawl4AIEngine()
        result = await engine.scrape("https://invalid.domain.xyz")
        assert result.content_type == "error"

    def test_engine_name(self):
        engine = Crawl4AIEngine()
        assert engine.name() == "crawl4ai"


class TestScrapeGraphAIEngine:
    @pytest.mark.asyncio
    async def test_scrape_with_llm(self, mock_llm, local_site):
        engine = ScrapeGraphAIEngine(llm=mock_llm)
        result = await engine.scrape(f"{local_site}/html", "extraer texto")
        assert result.content_type in ["structured", "text"]
        assert result.engine_used == "scrapegraph"

    @pytest.mark.asyncio
    async def test_scrape_without_llm(self, local_site):
        engine = ScrapeGraphAIEngine(llm=None)
        result = await engine.scrape(f"{local_site}/html")
        assert result.content_type == "text"


class TestFirecrawlEngine:
    @pytest.mark.asyncio
    async def test_scrape(self, local_site):
        engine = FirecrawlEngine()
        result = await engine.scrape(f"{local_site}/html")
        assert result.content_type == "text"
        assert result.engine_used == "firecrawl"


class TestEngineSelector:
    def test_select_default(self):
        engine = EngineSelector.select("https://example.com")
        assert isinstance(engine, Crawl4AIEngine)

    def test_select_with_query_and_llm(self):
        mock_llm = MagicMock()
        engine = EngineSelector.select("https://example.com", "test query", llm=mock_llm)
        assert isinstance(engine, ScrapeGraphAIEngine)

    def test_select_js_heavy(self):
        engine = EngineSelector.select("https://app.react.dev")
        assert isinstance(engine, FirecrawlEngine)


# ============================================================
# Tests: Pipeline
# ============================================================

class TestKnowledgeAcquisitionPipeline:
    @pytest.mark.asyncio
    async def test_acquire_with_urls(self, ems, local_site):
        pipeline = KnowledgeAcquisitionPipeline(ems)
        result = await pipeline.acquire(
            query="test",
            company_id="test-company",
            urls=[f"{local_site}/html"],
            max_sources=1,
        )
        assert result.sources_scraped == 1
        assert result.total_duration_ms > 0

    @pytest.mark.asyncio
    async def test_acquire_quality_filter(self, ems, local_site):
        pipeline = KnowledgeAcquisitionPipeline(ems)
        result = await pipeline.acquire(
            query="test",
            company_id="test-company",
            urls=[f"{local_site}/html"],
        )
        # la página local tiene contenido suficiente para pasar el filtro de calidad
        assert result.sources_succeeded == 1
        assert result.quality_scores and result.quality_scores[0] > 0.3

    @pytest.mark.asyncio
    async def test_acquire_with_mock_urls(self, ems, local_site):
        pipeline = KnowledgeAcquisitionPipeline(ems)
        result = await pipeline.acquire(
            query="bpo colombia",
            company_id="test-company",
            urls=[f"{local_site}/html"],
        )
        assert result.query == "bpo colombia"

    @pytest.mark.asyncio
    async def test_acquire_error_handling(self, ems):
        pipeline = KnowledgeAcquisitionPipeline(ems)
        result = await pipeline.acquire(
            query="test",
            company_id="test-company",
            urls=["https://invalid.domain.xyz"],
        )
        assert result.sources_failed >= 1
        assert len(result.errors) > 0


# ============================================================
# Tests: Integration with EMS
# ============================================================

class TestDKAIntegration:
    @pytest.mark.asyncio
    async def test_full_flow(self, ems, local_site):
        """Test completo: acquire → EMS → retrieve."""
        pipeline = KnowledgeAcquisitionPipeline(ems)

        # 1. Adquirir conocimiento
        result = await pipeline.acquire(
            query="información de prueba",
            company_id="test-company",
            urls=[f"{local_site}/html"],
        )

        # 2. Verificar que se almacenó (antes: `if` que pasaba en silencio sin red)
        assert result.sources_succeeded == 1

        # 3. Recuperar conocimiento
        retrieval = await ems.retrieve(
            company_id="test-company",
            query="mercado café especial Colombia",
        )
        assert any("café" in c["text"] for c in retrieval.chunks)

    @pytest.mark.asyncio
    async def test_acquire_stores_in_ems(self, ems, local_site):
        """Verifica que el conocimiento adquirido se almacena en EMS."""
        pipeline = KnowledgeAcquisitionPipeline(ems)

        result = await pipeline.acquire(
            query="datos de prueba",
            company_id="test-company",
            urls=[f"{local_site}/html"],
        )

        # Verificar stats del EMS
        stats = ems.get_stats("test-company")
        assert result.sources_succeeded == 1
        assert stats["documents"] >= 1


# ============================================================
# Tests: DKA como herramientas TEF (antes 0 % de cobertura)
# ============================================================

class TestDKATools:
    @pytest.fixture
    def tool_context(self):
        from app.tef.interfaces import ToolContext
        return ToolContext(company_id="c1", user_id="u1", trace_id="t1")

    @pytest.mark.asyncio
    async def test_crawl4ai_tool(self, local_site, tool_context):
        from app.dka.tools import Crawl4AITool
        tool = Crawl4AITool()
        assert tool.metadata().id == "crawl4ai"
        result = await tool.execute({"url": f"{local_site}/html"}, tool_context)
        assert result.status == "success"
        assert result.output["title"] == "Café Andino — Informe de mercado"
        assert result.output["word_count"] > 100

    @pytest.mark.asyncio
    async def test_scrapegraph_tool(self, local_site, tool_context, mock_llm):
        from app.dka.tools import ScrapeGraphTool
        tool = ScrapeGraphTool(llm=mock_llm)
        assert tool.metadata().id == "scrapegraph"
        result = await tool.execute({"url": f"{local_site}/html", "query": "precios"}, tool_context)
        assert result.status == "success"
        assert result.output["extracted_content"]

    @pytest.mark.asyncio
    async def test_firecrawl_tool(self, local_site, tool_context):
        from app.dka.tools import FirecrawlTool
        tool = FirecrawlTool()
        assert tool.metadata().id == "firecrawl"
        result = await tool.execute({"url": f"{local_site}/html"}, tool_context)
        assert result.status == "success"
        assert "café" in result.output["content"].lower()

    @pytest.mark.asyncio
    async def test_tools_block_internal_network(self, local_http_server, tool_context):
        """Sin el permiso del fixture local_site, la protección SSRF bloquea 127.0.0.1."""
        from app.dka.tools import Crawl4AITool, FirecrawlTool
        for tool in (Crawl4AITool(), FirecrawlTool()):
            result = await tool.execute({"url": f"{local_http_server}/html"}, tool_context)
            assert result.status == "error"
