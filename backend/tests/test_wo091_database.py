"""WO-091 — PostgreSQL + pgvector: vector store persistente y migraciones.

Corre en SQLite por defecto y contra PostgreSQL con TEST_DATABASE_URL.
"""
import asyncio

import pytest
from sqlalchemy import create_engine, inspect, text

from app.core.migrations import upgrade_database
from app.ems.factory import build_ems
from app.ems.models import EMSEmbedding
from app.ems.providers import VectorRecord
from app.ems.vector_store import SQLVectorStoreProvider


def _record(id_, vector, company="c1", doc="d1", text_=""):
    return VectorRecord(
        id=id_, vector=vector, text=text_ or id_,
        metadata={"company_id": company, "document_id": doc},
    )


class TestSQLVectorStore:
    def test_search_orders_by_cosine_similarity(self, db_session):
        store = SQLVectorStoreProvider(db_session)
        store.upsert([
            _record("a", [1.0, 0.0, 0.0]),
            _record("b", [0.7, 0.7, 0.0]),
            _record("c", [0.0, 0.0, 1.0]),
        ])
        db_session.commit()

        results = store.search([1.0, 0.0, 0.0], top_k=3, filter_metadata={"company_id": "c1"})
        assert [r.id for r in results] == ["a", "b", "c"]
        assert results[0].score == pytest.approx(1.0, abs=1e-6)
        assert results[2].score == pytest.approx(0.0, abs=1e-6)

    def test_search_isolates_companies_and_dimensions(self, db_session):
        store = SQLVectorStoreProvider(db_session)
        store.upsert([
            _record("mine", [1.0, 0.0], company="c1"),
            _record("other", [1.0, 0.0], company="c2"),
            _record("other-dim", [1.0, 0.0, 0.0], company="c1"),
        ])
        db_session.commit()

        results = store.search([1.0, 0.0], top_k=10, filter_metadata={"company_id": "c1"})
        assert [r.id for r in results] == ["mine"]

    def test_upsert_replaces_delete_and_count(self, db_session):
        store = SQLVectorStoreProvider(db_session)
        store.upsert([_record("x", [1.0, 0.0]), _record("y", [0.0, 1.0], company="c2")])
        store.upsert([_record("x", [0.0, 1.0], text_="actualizado")])
        db_session.commit()

        assert store.count() == 2
        assert store.count("c1") == 1
        assert db_session.get(EMSEmbedding, "x").content == "actualizado"

        assert store.delete(["x", "inexistente"]) == 1
        db_session.commit()
        assert store.count("c1") == 0


class TestSharedPersistentMemory:
    def test_knowledge_is_shared_across_ems_instances(self, db_session):
        """Antes cada router tenía su propio vector store en memoria."""
        ingest_ems = build_ems(db_session)  # p. ej. router /ems
        result = asyncio.run(ingest_ems.ingest(
            company_id="empresa-1",
            text="La empresa vende café orgánico de origen colombiano a cadenas de hoteles.",
            title="Modelo de negocio",
        ))
        assert result.status == "success"

        agent_ems = build_ems(db_session)  # p. ej. router /agents o /board
        retrieved = asyncio.run(agent_ems.retrieve("empresa-1", "café orgánico hoteles"))
        vector_hits = [c for c in retrieved.chunks if c["source"] == "vector_search"]
        assert vector_hits, "el conocimiento ingerido debe ser visible para otros módulos"
        assert "café" in vector_hits[0]["text"]

        assert agent_ems.get_stats("empresa-1")["vector_store_size"] == result.chunks_created

    def test_delete_document_removes_embeddings(self, db_session):
        ems = build_ems(db_session)
        result = asyncio.run(ems.ingest("empresa-2", "Texto efímero de prueba", "Temporal"))
        assert ems.get_stats("empresa-2")["vector_store_size"] > 0

        assert ems.delete_document(result.document_id) is True
        assert ems.get_stats("empresa-2")["vector_store_size"] == 0


class TestMigrations:
    def test_legacy_sqlite_database_is_adopted(self, tmp_path):
        """Una BD creada con create_all antes de WO-091 se marca y se actualiza."""
        url = f"sqlite:///{tmp_path / 'legacy.db'}"
        legacy = create_engine(url)
        with legacy.begin() as conn:
            conn.execute(text("CREATE TABLE users (id VARCHAR(36) PRIMARY KEY, email VARCHAR(255))"))
            conn.execute(text("INSERT INTO users VALUES ('u1', 'hernan@example.com')"))

        upgrade_database(legacy)

        tables = set(inspect(legacy).get_table_names())
        assert {"alembic_version", "ems_embeddings"} <= tables
        with legacy.connect() as conn:
            assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0002"
            assert conn.execute(text("SELECT email FROM users")).scalar() == "hernan@example.com"
        legacy.dispose()

    def test_fresh_database_gets_full_schema(self, tmp_path):
        engine = create_engine(f"sqlite:///{tmp_path / 'fresh.db'}")
        upgrade_database(engine)
        upgrade_database(engine)  # idempotente
        tables = set(inspect(engine).get_table_names())
        assert len(tables) == 34  # 33 tablas de dominio + alembic_version
        engine.dispose()


class TestSqliteToPostgresScript:
    @pytest.mark.skipif(
        not __import__("os").getenv("TEST_DATABASE_URL", "").startswith("postgresql"),
        reason="requiere TEST_DATABASE_URL de PostgreSQL",
    )
    def test_copies_all_rows(self, tmp_path):
        import os
        from sqlalchemy.orm import Session

        from app.core.auth import hash_password
        from app.models.models import Company, User
        from scripts.migrate_sqlite_to_postgres import migrate

        source_url = f"sqlite:///{tmp_path / 'laptop.db'}"
        source = create_engine(source_url)
        upgrade_database(source)
        with Session(source) as s:
            user = User(email="h@example.com", name="H", hashed_password=hash_password("x"))
            s.add(user)
            s.flush()
            s.add(Company(name="ACME", created_by=user.id, primary_user_id=user.id))
            SQLVectorStoreProvider(s).upsert([_record("e1", [0.6, 0.8], company="acme")])
            s.commit()
        source.dispose()

        copied = migrate(source_url, os.environ["TEST_DATABASE_URL"], force=True)
        assert copied["users"] == 1 and copied["companies"] == 1 and copied["ems_embeddings"] == 1

        target = create_engine(os.environ["TEST_DATABASE_URL"])
        with Session(target) as s:
            store = SQLVectorStoreProvider(s)
            hit = store.search([0.6, 0.8], filter_metadata={"company_id": "acme"})[0]
            assert hit.id == "e1" and hit.score == pytest.approx(1.0, abs=1e-6)
            assert s.query(User).one().role.value == "user"
        target.dispose()
