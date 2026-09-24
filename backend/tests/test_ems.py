"""
Tests para el Enterprise Memory System — WO-004.
"""

import pytest
from unittest.mock import MagicMock

from app.models.models import User, Company, Project, Level
from app.ems.providers import (
    LocalEmbeddingProvider, LocalVectorStoreProvider, VectorRecord
)
from app.ems.chunking import TextChunker, Chunk
from app.ems.ingestion import IngestionPipeline, IngestionResult
from app.ems.retrieval import HybridRetriever, RetrievalResult
from app.ems.memory import EnterpriseMemorySystem


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
def text_chunker():
    return TextChunker(chunk_size=100, chunk_overlap=10)


@pytest.fixture
def test_company(db_session):
    from app.core.auth import hash_password
    user = User(
        email="ems@test.com",
        name="EMS Tester",
        hashed_password=hash_password("test123"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()

    company = Company(
        name="EMS Test Corp",
        description="Test company for EMS",
        industry="technology",
        country="Argentina",
        maturity=0.5,
        primary_user_id=user.id,
        created_by=user.id,
    )
    db_session.add(company)
    db_session.commit()

    project = Project(company_id=company.id, name="EMS Project")
    db_session.add(project)
    db_session.commit()

    level = Level(project_id=project.id, number=1, name="El Dolor", status="active")
    db_session.add(level)
    db_session.commit()

    return company, user


# ============================================================
# Tests: Providers
# ============================================================

class TestProviders:
    def test_local_embedding_provider(self):
        provider = LocalEmbeddingProvider(dim=64)
        assert provider.dimension() == 64

        vectors = provider.embed(["hello world", "test text"])
        assert len(vectors) == 2
        assert len(vectors[0]) == 64
        assert len(vectors[1]) == 64

    def test_local_embedding_query(self):
        provider = LocalEmbeddingProvider(dim=64)
        vec = provider.embed_query("test query")
        assert len(vec) == 64

    def test_local_vector_store_upsert(self):
        store = LocalVectorStoreProvider()
        records = [
            VectorRecord(id="1", vector=[1.0, 0.0, 0.0], text="test1"),
            VectorRecord(id="2", vector=[0.0, 1.0, 0.0], text="test2"),
        ]
        count = store.upsert(records)
        assert count == 2
        assert store.count() == 2

    def test_local_vector_store_search(self):
        store = LocalVectorStoreProvider()
        store.upsert([
            VectorRecord(id="1", vector=[1.0, 0.0], text="hello"),
            VectorRecord(id="2", vector=[0.0, 1.0], text="world"),
        ])
        results = store.search([1.0, 0.0], top_k=1)
        assert len(results) == 1
        assert results[0].id == "1"
        assert results[0].score > 0.9

    def test_local_vector_store_delete(self):
        store = LocalVectorStoreProvider()
        store.upsert([VectorRecord(id="1", vector=[1.0], text="t")])
        assert store.count() == 1
        store.delete(["1"])
        assert store.count() == 0

    def test_local_vector_store_filter(self):
        store = LocalVectorStoreProvider()
        store.upsert([
            VectorRecord(id="1", vector=[1.0, 0.0], text="a", metadata={"company": "A"}),
            VectorRecord(id="2", vector=[1.0, 0.0], text="b", metadata={"company": "B"}),
        ])
        results = store.search([1.0, 0.0], top_k=10, filter_metadata={"company": "A"})
        assert len(results) == 1
        assert results[0].metadata["company"] == "A"


# ============================================================
# Tests: Chunking
# ============================================================

class TestChunking:
    def test_chunk_short_text(self):
        chunker = TextChunker(chunk_size=100)
        chunks = chunker.chunk("Hello world")
        assert len(chunks) == 1
        assert chunks[0].content == "Hello world"

    def test_chunk_long_text(self):
        chunker = TextChunker(chunk_size=10, chunk_overlap=2, min_chunk_size=5)
        text = " ".join([f"word{i}" for i in range(50)])
        chunks = chunker.chunk(text)
        assert len(chunks) > 1

    def test_chunk_empty_text(self):
        chunker = TextChunker()
        chunks = chunker.chunk("")
        assert len(chunks) == 0

    def test_chunk_content_hash(self):
        chunker = TextChunker()
        chunks = chunker.chunk("Test content for hashing")
        assert len(chunks[0].content_hash) == 16

    def test_chunk_metadata(self):
        chunker = TextChunker()
        chunks = chunker.chunk("Test", metadata={"doc_id": "123"})
        assert chunks[0].metadata["doc_id"] == "123"


# ============================================================
# Tests: Ingestion Pipeline
# ============================================================

class TestIngestionPipeline:
    @pytest.mark.asyncio
    async def test_ingest_text(self, db_session, embedding_provider, vector_store, test_company):
        company, _ = test_company
        pipeline = IngestionPipeline(db_session, embedding_provider, vector_store)

        result = await pipeline.ingest_text(
            company_id=str(company.id),
            text="Esta es una prueba de ingesta de documento con suficiente texto para generar chunks.",
            title="Documento de Prueba",
            source_type="text",
        )

        assert result.status == "success"
        assert result.document_id != ""
        assert result.chunks_created >= 1
        assert result.embeddings_generated >= 1
        assert result.vector_records_upserted >= 1

    @pytest.mark.asyncio
    async def test_ingest_and_list(self, db_session, embedding_provider, vector_store, test_company):
        company, _ = test_company
        pipeline = IngestionPipeline(db_session, embedding_provider, vector_store)

        await pipeline.ingest_text(
            company_id=str(company.id),
            text="Documento uno con contenido de prueba.",
            title="Doc 1",
        )
        await pipeline.ingest_text(
            company_id=str(company.id),
            text="Documento dos con otro contenido.",
            title="Doc 2",
        )

        docs = pipeline.list_documents(str(company.id))
        assert len(docs) == 2

    @pytest.mark.asyncio
    async def test_ingest_creates_chunks(self, db_session, embedding_provider, vector_store, test_company):
        company, _ = test_company
        pipeline = IngestionPipeline(db_session, embedding_provider, vector_store)

        result = await pipeline.ingest_text(
            company_id=str(company.id),
            text="Texto de prueba " * 100,
            title="Doc Large",
        )

        chunks = pipeline.get_document_chunks(result.document_id)
        assert len(chunks) >= 1


# ============================================================
# Tests: Retrieval
# ============================================================

class TestRetrieval:
    @pytest.mark.asyncio
    async def test_retrieve_after_ingest(self, db_session, embedding_provider, vector_store, test_company):
        company, _ = test_company

        # Ingestar
        pipeline = IngestionPipeline(db_session, embedding_provider, vector_store)
        await pipeline.ingest_text(
            company_id=str(company.id),
            text="TechStartup Argentina es una empresa de tecnología SaaS que vende software para PYMEs en Latinoamérica.",
            title="Company Info",
        )

        # Recuperar
        retriever = HybridRetriever(db_session, embedding_provider, vector_store)
        result = await retriever.retrieve(
            company_id=str(company.id),
            query="¿Qué hace la empresa?",
        )

        assert result.total_results >= 1
        assert len(result.context_text) > 0

    @pytest.mark.asyncio
    async def test_retrieve_returns_facts(self, db_session, embedding_provider, vector_store, test_company):
        company, _ = test_company

        # Agregar hecho
        from app.ems.models import KnowledgeFact
        fact = KnowledgeFact(
            company_id=str(company.id),
            fact_type="entity",
            subject="TechStartup",
            predicate="opera en",
            object_value="Latinoamérica",
            confidence=0.9,
        )
        db_session.add(fact)
        db_session.commit()

        # Recuperar
        retriever = HybridRetriever(db_session, embedding_provider, vector_store)
        result = await retriever.retrieve(
            company_id=str(company.id),
            query="¿Dónde opera la empresa?",
        )

        assert len(result.facts) >= 1


# ============================================================
# Tests: Enterprise Memory System
# ============================================================

class TestEnterpriseMemorySystem:
    @pytest.mark.asyncio
    async def test_full_cycle(self, db_session, embedding_provider, vector_store, test_company):
        """Test completo: ingestar → recuperar → estadísticas."""
        company, _ = test_company

        ems = EnterpriseMemorySystem(db_session, embedding_provider, vector_store)

        # 1. Ingestar
        result = await ems.ingest(
            company_id=str(company.id),
            text="TechStartup Argentina fue fundada en 2024. Desarrolla software SaaS para PYMEs. Tiene 5 empleados. Facturó $100K en 2025.",
            title="Empresa Info",
            source_type="text",
        )
        assert result.status == "success"

        # 2. Recuperar
        retrieval = await ems.retrieve(
            company_id=str(company.id),
            query="¿Cuántos empleados tiene la empresa?",
        )
        assert retrieval.total_results >= 1

        # 3. Agregar hecho
        fact = ems.add_fact(
            company_id=str(company.id),
            fact_type="metric",
            subject="TechStartup",
            predicate="tiene",
            object_value="5 empleados",
            confidence=0.95,
        )
        assert fact.id is not None

        # 4. Obtener hechos
        facts = ems.get_facts(str(company.id))
        assert len(facts) >= 1

        # 5. Estadísticas
        stats = ems.get_stats(str(company.id))
        assert stats["documents"] >= 1
        assert stats["chunks"] >= 1
        assert stats["facts"] >= 1

    @pytest.mark.asyncio
    async def test_correction_flow(self, db_session, embedding_provider, vector_store, test_company):
        """Test de flujo de corrección."""
        company, _ = test_company
        ems = EnterpriseMemorySystem(db_session, embedding_provider, vector_store)

        # Agregar hecho
        fact = ems.add_fact(
            company_id=str(company.id),
            fact_type="metric",
            subject="TechStartup",
            predicate="tiene",
            object_value="3 empleados",
            confidence=0.9,
        )

        # Registrar corrección
        correction = ems.record_correction(
            company_id=str(company.id),
            original_text="3 empleados",
            corrected_text="5 empleados",
            fact_id=fact.id,
            reason="Dato desactualizado",
        )
        assert correction.id is not None

        # Verificar que la confianza se ajustó
        db_session.refresh(fact)
        assert fact.confidence < 0.9

    @pytest.mark.asyncio
    async def test_delete_document(self, db_session, embedding_provider, vector_store, test_company):
        company, _ = test_company
        ems = EnterpriseMemorySystem(db_session, embedding_provider, vector_store)

        result = await ems.ingest(
            company_id=str(company.id),
            text="Documento a eliminar con suficiente contenido.",
            title="Delete Me",
        )

        deleted = ems.delete_document(result.document_id)
        assert deleted is True

        doc = ems.get_document(result.document_id)
        assert doc is None


# ============================================================
# Tests: Integration with Cognitive System
# ============================================================

class TestEMSIntegration:
    @pytest.mark.asyncio
    async def test_ems_provides_context_to_llm(self, db_session, embedding_provider, vector_store, test_company):
        """Verifica que el EMS puede proveer contexto para el LLM."""
        company, _ = test_company
        ems = EnterpriseMemorySystem(db_session, embedding_provider, vector_store)

        # Ingestar información
        await ems.ingest(
            company_id=str(company.id),
            text="TechStartup opera en Argentina. Su mercado principal son las PYMEs tecnológicas. Facturó $100K en 2025.",
            title="Company Context",
        )

        # Obtener contexto para LLM
        context = await ems.retrieve_for_llm(
            company_id=str(company.id),
            query="¿Cuál es el mercado de la empresa?",
        )

        assert len(context) > 0
        assert "TechStartup" in context or "PYMEs" in context or "CONOCIMIENTO" in context
