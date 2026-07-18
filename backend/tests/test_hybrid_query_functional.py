"""Funcional: GET /kg/query (hibrida) contra Ollama+Postgres reales, via la API HTTP."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.auth.jwt import create_access_token, hash_password
from app.db import SessionLocal
from app.embeddings import embed_text
from app.main import app
from app.models.kg import KGAristaBackend, KGNodoBackend, MemoriaSemanticaBackend
from app.models.usuario import Usuario

pytestmark = pytest.mark.functional


@pytest.fixture
def authed_client():
    db = SessionLocal()
    unique = uuid.uuid4().hex[:8]
    email = f"hybrid-test-{unique}@adan-demo.io"
    user = Usuario(email=email, hashed_password=hash_password("x"))
    db.add(user)
    db.commit()
    token = create_access_token(email)
    client = TestClient(app)
    client.headers["Authorization"] = f"Bearer {token}"
    try:
        yield client
    finally:
        db.delete(user)
        db.commit()
        db.close()


def test_hybrid_query_endpoint_rescues_graph_fact(authed_client: TestClient) -> None:
    from datetime import UTC, datetime

    db = SessionLocal()
    node_a = KGNodoBackend(tipo="hecho", nombre="El proveedor aumento tarifas", created_at=datetime.now(UTC))
    node_b = KGNodoBackend(
        tipo="hecho", nombre="Se busco un proveedor alternativo en otro pais", created_at=datetime.now(UTC)
    )
    db.add_all([node_a, node_b])
    db.flush()
    edge = KGAristaBackend(
        origen_id=node_a.id, destino_id=node_b.id, tipo_relacion="genero_decision", created_at=datetime.now(UTC)
    )
    db.add(edge)

    embedding = embed_text(node_a.nombre)
    memoria = MemoriaSemanticaBackend(
        contenido=node_a.nombre, origen="hecho", embedding=embedding, nodo_id=node_a.id, created_at=datetime.now(UTC)
    )
    db.add(memoria)
    db.commit()

    try:
        resp = authed_client.get("/kg/query", params={"q": "que paso con las tarifas del proveedor"})
        assert resp.status_code == 200
        results = resp.json()
        origins = {r["origen"] for r in results}
        assert "semantico" in origins
        contenidos = [r["contenido"] for r in results]
        assert any("proveedor" in c.lower() for c in contenidos)
        assert any("alternativo" in c.lower() for c in contenidos)  # rescatado por grafo
    finally:
        # DELETE crudo, en el orden explicito correcto (aristas y memoria antes que
        # nodos) - db.delete() de objetos ORM sin relationship()/ForeignKey() declarada
        # entre estas clases (a proposito, ver models/kg.py) deja que SQLAlchemy decida
        # el orden de flush, que puede violar la FK real de Postgres.
        db.execute(text("DELETE FROM memoria_semantica WHERE id = :id"), {"id": memoria.id})
        db.execute(text("DELETE FROM kg_aristas WHERE id = :id"), {"id": edge.id})
        db.execute(text("DELETE FROM kg_nodos WHERE id IN (:a, :b)"), {"a": node_a.id, "b": node_b.id})
        db.commit()
        db.close()
