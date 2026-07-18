"""Funcional: chunking + embeddings reales (Ollama) + busqueda por similitud real
(pgvector) contra Postgres real. BP-0007 (AD-CMP-04 memoria semantica)."""

import uuid

import pytest
from sqlalchemy import text

from db import SessionLocal
from memory.chunking import chunk_text
from memory.ingestion import ingest_text
from memory.models import MemoriaSemantica
from memory.search import semantic_search
from models.ollama_adapter import OllamaBackend

pytestmark = pytest.mark.functional


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


def _create_real_proyecto(db) -> uuid.UUID:
    """Ver test_kg_repository_functional.py - mismo helper, FK real a proyectos.id."""
    unique = uuid.uuid4().hex[:8]
    usuario_id, empresa_id, proyecto_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    db.execute(
        text(
            "INSERT INTO usuarios (id, email, hashed_password, status, created_at, updated_at) "
            "VALUES (:id, :email, 'x', 'active', now(), now())"
        ),
        {"id": usuario_id, "email": f"mem-test-{unique}@adan-demo.io"},
    )
    db.execute(
        text(
            "INSERT INTO empresas (id, razon_social, status, created_at, updated_at) "
            "VALUES (:id, :nombre, 'active', now(), now())"
        ),
        {"id": empresa_id, "nombre": f"Mem Test Co. {unique}"},
    )
    db.execute(
        text(
            "INSERT INTO proyectos (id, empresa_id, usuario_principal_id, status, created_at, updated_at) "
            "VALUES (:id, :empresa_id, :usuario_id, 'active', now(), now())"
        ),
        {"id": proyecto_id, "empresa_id": empresa_id, "usuario_id": usuario_id},
    )
    db.flush()
    return proyecto_id


@pytest.fixture
def backend() -> OllamaBackend:
    return OllamaBackend()


def test_chunk_text_short_and_long():
    assert chunk_text("") == []
    assert chunk_text("texto corto") == ["texto corto"]

    long_text = "\n\n".join([f"Parrafo numero {i} con algo de contenido de relleno." for i in range(50)])
    chunks = chunk_text(long_text, chunk_size=200, overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 250 for c in chunks)  # margen por el parrafo mas largo posible


def test_ingest_and_semantic_search_real(db, backend: OllamaBackend) -> None:
    rows = ingest_text(
        db,
        backend,
        "Paradixe es una empresa de tecnologia que construye software para otras empresas. "
        "El equipo trabaja principalmente con inteligencia artificial y agentes conversacionales.",
        origen="documento",
    )
    db.flush()
    assert len(rows) >= 1

    results = semantic_search(db, backend, "empresa de software e inteligencia artificial", top_k=3)

    assert len(results) >= 1
    top_result, distance = results[0]
    assert isinstance(top_result, MemoriaSemantica)
    assert 0.0 <= distance <= 2.0  # rango valido de distancia coseno
    assert "Paradixe" in top_result.contenido or "tecnologia" in top_result.contenido


def test_semantic_search_isolated_by_proyecto(db, backend: OllamaBackend) -> None:
    proyecto_a = _create_real_proyecto(db)
    proyecto_b = _create_real_proyecto(db)

    ingest_text(db, backend, "Contenido exclusivo del proyecto A sobre finanzas.", "documento", proyecto_id=proyecto_a)
    ingest_text(db, backend, "Contenido exclusivo del proyecto B sobre marketing.", "documento", proyecto_id=proyecto_b)
    db.flush()

    results_a = semantic_search(db, backend, "finanzas", proyecto_id=proyecto_a, top_k=5)
    assert all(r.proyecto_id == proyecto_a for r, _ in results_a)
