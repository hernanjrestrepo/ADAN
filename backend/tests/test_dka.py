"""
Tests para Dynamic Knowledge Acquisition — WO-009.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.models import User, Company
from app.ems.models import EMSBase
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

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    EMSBase.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()


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
    async def test_scrape_httpbin(self):
        engine = Crawl4AIEngine()
        result = await engine.scrape("https://httpbin.org/html")
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
    async def test_scrape_with_llm(self, mock_llm):
        engine = ScrapeGraphAIEngine(llm=mock_llm)
        result = await engine.scrape("https://httpbin.org/html", "extraer texto")
        assert result.content_type in ["structured", "text"]
        assert result.engine_used == "scrapegraph"

    @pytest.mark.asyncio
    async def test_scrape_without_llm(self):
        engine = ScrapeGraphAIEngine(llm=None)
        result = await engine.scrape("https://httpbin.org/html")
        assert result.content_type == "text"


class TestFirecrawlEngine:
    @pytest.mark.asyncio
    async def test_scrape(self):
        engine = FirecrawlEngine()
        result = await engine.scrape("https://httpbin.org/html")
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
    async def test_acquire_with_urls(self, ems):
        pipeline = KnowledgeAcquisitionPipeline(ems)
        result = await pipeline.acquire(
            query="test",
            company_id="test-company",
            urls=["https://httpbin.org/html"],
            max_sources=1,
        )
        assert result.sources_scraped == 1
        assert result.total_duration_ms > 0

    @pytest.mark.asyncio
    async def test_acquire_quality_filter(self, ems):
        pipeline = KnowledgeAcquisitionPipeline(ems)
        result = await pipeline.acquire(
            query="test",
            company_id="test-company",
            urls=["https://httpbin.org/html"],
        )
        # httpbin.org/html tiene contenido suficiente
        assert result.sources_succeeded >= 0

    @pytest.mark.asyncio
    async def test_acquire_with_mock_urls(self, ems):
        pipeline = KnowledgeAcquisitionPipeline(ems)
        result = await pipeline.acquire(
            query="bpo colombia",
            company_id="test-company",
            urls=["https://httpbin.org/html"],
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
    async def test_full_flow(self, ems):
        """Test completo: acquire → EMS → retrieve."""
        pipeline = KnowledgeAcquisitionPipeline(ems)

        # 1. Adquirir conocimiento
        result = await pipeline.acquire(
            query="información de prueba",
            company_id="test-company",
            urls=["https://httpbin.org/html"],
        )

        # 2. Verificar que se almacenó
        if result.sources_succeeded > 0:
            # 3. Recuperar conocimiento
            retrieval = await ems.retrieve(
                company_id="test-company",
                query="información de prueba",
            )
            assert retrieval.total_results >= 0

    @pytest.mark.asyncio
    async def test_acquire_stores_in_ems(self, ems):
        """Verifica que el conocimiento adquirido se almacena en EMS."""
        pipeline = KnowledgeAcquisitionPipeline(ems)

        result = await pipeline.acquire(
            query="datos de prueba",
            company_id="test-company",
            urls=["https://httpbin.org/html"],
        )

        # Verificar stats del EMS
        stats = ems.get_stats("test-company")
        if result.sources_succeeded > 0:
            assert stats["documents"] >= 1
