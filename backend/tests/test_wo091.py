"""WO-091 — PostgreSQL + pgvector, una sola base declarativa, Alembic y migración de datos.

Las pruebas marcadas `requires_pg` corren con TEST_DATABASE_URL apuntando a PostgreSQL:

    TEST_DATABASE_URL=postgresql://postgres@127.0.0.1:5433/adan_test pytest tests/test_wo091.py
"""
import os
import uuid

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.core.config import normalize_database_url
from app.core.database import Base, import_all_models, make_engine
from app.core.migrations import INITIAL_REVISION, alembic_config, include_object_for, run_migrations
from app.core.sqlite_to_postgres import migrate
from app.ems.memory import EnterpriseMemorySystem
from app.ems.models import EMSChunk, EMSChunkEmbedding, EMSDocument
from app.ems.pgvector_store import PgVectorStoreProvider
from app.ems.providers import LocalEmbeddingProvider, OllamaEmbeddingProvider, VectorRecord
from app.ems.store import describe_providers, get_vector_store
from app.models.models import Company, Event, Project, User
from app.oos.models import DecisionRecord, Organization, WorkOrder

PG_URL = os.getenv("TEST_DATABASE_URL", "")
HEAD_REVISION = "0003"
requires_pg = pytest.mark.skipif(
    not PG_URL.startswith("postgres"), reason="requiere TEST_DATABASE_URL de PostgreSQL"
)


def _schema_diff(engine):
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn, opts={
            "compare_type": True, "include_object": include_object_for(engine.dialect.name),
        })
        return compare_metadata(ctx, Base.metadata)


def _version(engine):
    with engine.connect() as conn:
        return conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()


@pytest.fixture
def fresh_pg_url():
    """Una base PostgreSQL vacía y descartable en el mismo servidor de TEST_DATABASE_URL."""
    admin = make_engine(normalize_database_url(PG_URL)).execution_options(isolation_level="AUTOCOMMIT")
    name = f"adan_wo091_{uuid.uuid4().hex[:8]}"
    with admin.connect() as conn:
        conn.execute(text(f'CREATE DATABASE "{name}"'))
    yield admin.url.set(database=name).render_as_string(hide_password=False)
    with admin.connect() as conn:
        conn.execute(text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = :n"),
                     {"n": name})
        conn.execute(text(f'DROP DATABASE "{name}"'))
    admin.dispose()


# ============================================================
# Una sola base declarativa
# ============================================================

def test_single_declarative_base():
    import_all_models()
    tables = set(Base.metadata.tables)
    assert {"users", "companies", "ems_documents", "ems_chunk_embeddings", "oos_work_orders",
            "integration_connections", "tef_audit_log"} <= tables
    assert len(tables) == 36  # + llm_usage (WO-099)
    assert EMSDocument.metadata is Base.metadata and WorkOrder.metadata is Base.metadata


def test_database_url_is_normalized_to_psycopg():
    assert normalize_database_url("postgres://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert normalize_database_url("postgresql://u@h/db") == "postgresql+psycopg://u@h/db"
    assert normalize_database_url("sqlite:///x.db") == "sqlite:///x.db"


# ============================================================
# Migraciones de Alembic
# ============================================================

def test_migrations_build_the_model_schema_on_sqlite(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path}/adan.db")
    run_migrations(engine)
    assert _version(engine) == HEAD_REVISION
    assert _schema_diff(engine) == []
    run_migrations(engine)  # idempotente
    engine.dispose()


@requires_pg
def test_migrations_build_the_model_schema_on_postgres(fresh_pg_url):
    engine = make_engine(normalize_database_url(fresh_pg_url))
    run_migrations(engine)
    assert _version(engine) == HEAD_REVISION
    assert _schema_diff(engine) == []
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).scalar() == 1
        index = conn.execute(text(
            "SELECT indexdef FROM pg_indexes WHERE indexname = 'idx_ems_embedding_hnsw'")).scalar()
        assert "hnsw" in index and "vector_cosine_ops" in index
        # Enums como texto: agregar un valor no exige alterar un tipo de PostgreSQL
        assert conn.execute(text("SELECT count(*) FROM pg_type WHERE typname = 'entitystatus'")).scalar() == 0
    engine.dispose()


def test_legacy_database_is_adopted_without_losing_data(tmp_path):
    """Una base creada con create_all antes de WO-091 se adopta como 0001."""
    engine = make_engine(f"sqlite:///{tmp_path}/legacy.db")
    with engine.begin() as conn:
        command.upgrade(alembic_config(conn), INITIAL_REVISION)
        # Así quedaba una base de antes de WO-091: sin Alembic y sin embeddings
        conn.execute(text("DROP TABLE alembic_version"))
        conn.execute(text("DROP TABLE ems_chunk_embeddings"))
        conn.execute(text("INSERT INTO users (id, email, name, hashed_password, role, status, version, "
                          "created_at, updated_at) VALUES ('u1', 'antes@example.com', 'Antes', 'x', "
                          "'USER', 'ACTIVE', 1, '2026-01-01 00:00:00', '2026-01-01 00:00:00')"))

    run_migrations(engine)

    assert _version(engine) == HEAD_REVISION
    assert "ems_chunk_embeddings" in inspect(engine).get_table_names()
    assert _schema_diff(engine) == []
    with Session(engine) as db:
        assert db.query(User).filter_by(email="antes@example.com").count() == 1
    engine.dispose()


# ============================================================
# Tipos: texto largo, enums, JSON
# ============================================================

def test_long_llm_text_is_truncated_instead_of_failing(db_session):
    """PostgreSQL hace cumplir String(n). Un título largo del LLM no debe tumbar el OOS."""
    org = Organization(company_id="c1", name="Org")
    db_session.add(org)
    db_session.flush()
    wo = WorkOrder(organization_id=org.id, title="acción " * 100, description="detalle " * 1000)
    db_session.add(wo)
    db_session.commit()
    db_session.refresh(wo)
    assert len(wo.title) == 500
    assert len(wo.description) == len("detalle " * 1000)  # Text no se recorta


def test_enums_and_json_round_trip(db_session):
    user = User(email="enum@example.com", name="E", hashed_password="x")
    db_session.add(user)
    db_session.flush()
    company = Company(name="Acme", created_by=user.id, primary_user_id=user.id)
    db_session.add(company)
    db_session.flush()
    project = Project(company_id=company.id, name="P")
    db_session.add(project)
    db_session.flush()
    db_session.add(Event(project_id=project.id, event_type="t", entity_type="e", entity_id="1",
                         data={"votos": [1, 2], "ñ": "sí"}))
    db_session.commit()

    raw_role = db_session.execute(text("SELECT role FROM users WHERE email = 'enum@example.com'")).scalar()
    assert raw_role == "USER"
    assert db_session.query(Event).one().data == {"votos": [1, 2], "ñ": "sí"}


# ============================================================
# Embeddings y pgvector
# ============================================================

def test_ollama_embedding_provider_checks_dimension(monkeypatch):
    calls = []

    class FakeResponse:
        def __init__(self, vectors):
            self._vectors = vectors

        def raise_for_status(self):
            pass

        def json(self):
            return {"embeddings": self._vectors}

    def fake_post(url, json, timeout):
        calls.append((url, json))
        return FakeResponse([[0.1] * dim for _ in json["input"]])

    import httpx
    monkeypatch.setattr(httpx, "post", fake_post)
    dim = 768
    provider = OllamaEmbeddingProvider("http://ollama:11434/", "nomic-embed-text", 768)
    assert len(provider.embed(["a", "b"])) == 2
    assert calls[0] == ("http://ollama:11434/api/embed", {"model": "nomic-embed-text", "input": ["a", "b"]})
    assert provider.model_name == "nomic-embed-text"

    dim = 384  # un modelo distinto al configurado
    with pytest.raises(ValueError):
        provider.embed(["a"])


@requires_pg
def test_shared_store_is_pgvector_on_postgres(db_session):
    assert isinstance(get_vector_store(db_session), PgVectorStoreProvider)
    assert describe_providers(db_session)["vector_store"] == "PgVectorStoreProvider"


@requires_pg
@pytest.mark.asyncio
async def test_pgvector_search_is_per_company_and_skips_archived(db_session):
    embedder = LocalEmbeddingProvider(dim=768)
    ems = EnterpriseMemorySystem(db_session, embedder, PgVectorStoreProvider(db_session, embedder.model_name))
    mine = await ems.ingest("empresa-a", "Las panaderías pierden pan cada día por hornear de más.", "Pan A")
    await ems.ingest("empresa-b", "Las panaderías pierden pan cada día por hornear de más.", "Pan B")

    # Los vectores quedaron en la base, con su modelo
    rows = db_session.query(EMSChunkEmbedding).all()
    assert {r.company_id for r in rows} == {"empresa-a", "empresa-b"}
    assert {r.embedding_model for r in rows} == {"local-hash-768"}

    found = await ems.retrieve("empresa-a", "panaderías pan hornear")
    vector_hits = [c for c in found.chunks if c["source"] == "vector_search"]
    assert vector_hits and all(c["metadata"]["company_id"] == "empresa-a" for c in vector_hits)
    assert ems.get_stats("empresa-a")["vector_store_size"] == 1

    assert ems.delete_document(mine.document_id)
    found = await ems.retrieve("empresa-a", "panaderías pan hornear")
    assert not [c for c in found.chunks if c["source"] == "vector_search"]
    assert db_session.get(EMSDocument, mine.document_id).status == "archived"


@requires_pg
def test_vectors_from_another_model_are_ignored(db_session):
    doc = EMSDocument(company_id="c", title="Doc", source_type="text", status="processed")
    db_session.add(doc)
    db_session.flush()
    chunk = EMSChunk(document_id=doc.id, company_id="c", chunk_index=0, content="texto")
    db_session.add(chunk)
    db_session.flush()
    PgVectorStoreProvider(db_session, "otro-modelo").upsert([
        VectorRecord(id=chunk.id, vector=[0.1] * 768, metadata={"document_id": doc.id, "company_id": "c"}),
    ])
    db_session.commit()
    store = PgVectorStoreProvider(db_session, "local-hash-768")
    assert store.search([0.1] * 768, filter_metadata={"company_id": "c"}) == []


# ============================================================
# Migración de datos SQLite → PostgreSQL
# ============================================================

def _seed_sqlite(path):
    engine = make_engine(f"sqlite:///{path}")
    run_migrations(engine)
    with Session(engine) as db:
        user = User(email="dueno@example.com", name="Dueño", hashed_password="hash")
        db.add(user)
        db.flush()
        company = Company(name="Panadería", created_by=user.id, primary_user_id=user.id)
        db.add(company)
        db.flush()
        project = Project(company_id=company.id, name="Proyecto")
        db.add(project)
        db.flush()
        db.add(Event(project_id=project.id, event_type="board", entity_type="decision", entity_id="d",
                     data={"consensus": {"decision": "NO_CONSENSUS"}}))
        doc = EMSDocument(company_id=company.id, title="Nota", source_type="text", status="processed")
        db.add(doc)
        db.flush()
        db.add(EMSChunk(document_id=doc.id, company_id=company.id, chunk_index=0, content="pan del día"))
        org = Organization(company_id=company.id, name="Org")
        db.add(org)
        db.flush()
        decision = DecisionRecord(organization_id=org.id, topic="Tema", final_decision="PROCEED",
                                  actions=[{"action": "Hornear menos"}])
        db.add(decision)
        db.flush()
        db.add(WorkOrder(organization_id=org.id, decision_id=decision.id, title="Hornear menos"))
        db.commit()
    engine.dispose()


@requires_pg
def test_sqlite_data_is_copied_to_postgres(tmp_path, fresh_pg_url):
    source = f"sqlite:///{tmp_path}/origen.db"
    _seed_sqlite(tmp_path / "origen.db")

    counts = migrate(source, fresh_pg_url)

    assert counts["users"] == 1 and counts["events"] == 1 and counts["oos_work_orders"] == 1
    assert counts["ems_chunk_embeddings"] == 1  # recalculado en pgvector
    src, dst = make_engine(source), make_engine(normalize_database_url(fresh_pg_url))
    with src.connect() as a, dst.connect() as b:
        for table in Base.metadata.sorted_tables:
            if table.name == "ems_chunk_embeddings":
                continue
            order = list(table.primary_key.columns)
            rows_a = [dict(r) for r in a.execute(select(table).order_by(*order)).mappings()]
            rows_b = [dict(r) for r in b.execute(select(table).order_by(*order)).mappings()]
            assert rows_a == rows_b, table.name
    src.dispose()
    dst.dispose()

    with pytest.raises(ValueError, match="no está vacío"):
        migrate(source, fresh_pg_url)
