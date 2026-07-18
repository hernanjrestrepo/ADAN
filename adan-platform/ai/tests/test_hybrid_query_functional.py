"""Funcional: consulta hibrida (semantica + grafo) contra Ollama+Postgres reales."""

import pytest

from db import SessionLocal
from memory.hybrid_query import hybrid_query
from memory.ingestion import ingest_text
from memory.repository import create_edge, create_node
from models.ollama_adapter import OllamaBackend

pytestmark = pytest.mark.functional


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def backend() -> OllamaBackend:
    return OllamaBackend()


def test_hybrid_query_rescues_graph_connected_fact(db, backend: OllamaBackend) -> None:
    # Un nodo semanticamente encontrable (menciona "precios de la competencia")...
    node_competencia = create_node(db, tipo="hecho", nombre="El competidor subio sus precios este mes")
    # ...conectado en el grafo a un hecho que NO se parece semanticamente al query...
    node_decision = create_node(db, tipo="hecho", nombre="Se pospuso la campana de descuentos de diciembre")
    create_edge(db, node_competencia.id, node_decision.id, "genero_decision")
    db.flush()

    # Se indexa semanticamente solo el primer hecho, ligado a su nodo del grafo.
    ingest_text(db, backend, node_competencia.nombre, origen="hecho", nodo_id=node_competencia.id)
    db.flush()

    results = hybrid_query(db, backend, "que esta haciendo la competencia con sus precios")

    origins = {r.origen for r in results}
    assert "semantico" in origins
    contenidos = [r.contenido for r in results]
    assert any("competidor" in c.lower() for c in contenidos)
    # El hecho conectado por grafo debe aparecer, aunque su texto no se parezca al query
    assert any("campana de descuentos" in c.lower() for c in contenidos)

    # El resultado semantico directo debe rankear mejor (distancia menor) que el de grafo
    semantic_result = next(r for r in results if r.origen == "semantico")
    graph_result = next(r for r in results if r.origen == "grafo")
    assert semantic_result.distance < graph_result.distance
