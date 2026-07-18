"""Funcional: herramientas de Agente (kg_read/kg_write/memory_search/memory_store) con
permisos, contra Postgres+Ollama reales. WO-003 Sprint 4."""

import pytest

from agents.tools import AgentTools, ToolPermissionError
from db import SessionLocal
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


def test_tool_denied_without_permission(db, backend: OllamaBackend) -> None:
    tools = AgentTools(db=db, model_backend=backend, agent_id="agente-restringido", allowed_tools=["memory_search"])

    with pytest.raises(ToolPermissionError):
        tools.kg_write(tipo="hecho", nombre="No deberia poder escribir esto")


def test_kg_write_and_read_with_permission(db, backend: OllamaBackend) -> None:
    tools = AgentTools(
        db=db, model_backend=backend, agent_id="agente-completo",
        allowed_tools=["kg_read", "kg_write", "memory_search", "memory_store"],
    )

    node_id = tools.kg_write(tipo="hecho", nombre="Hecho creado por herramienta real")
    db.flush()

    result = tools.kg_read(node_id)
    node_names = {n.nombre for n in result["nodos"]}
    assert "Hecho creado por herramienta real" in node_names


def test_memory_store_and_search_with_permission(db, backend: OllamaBackend) -> None:
    tools = AgentTools(
        db=db, model_backend=backend, agent_id="agente-memoria", allowed_tools=["memory_search", "memory_store"]
    )

    count = tools.memory_store("La empresa vende software a otras empresas.", origen="hecho")
    db.flush()
    assert count >= 1

    results = tools.memory_search("que vende la empresa")
    assert len(results) >= 1
