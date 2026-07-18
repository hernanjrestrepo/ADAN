"""Funcional: el MemoryHook del executor usa memoria semantica real cuando el Agente
tiene permiso - cierra el punto que WO-002 Sprint 2 dejo sin implementacion. WO-003
Sprint 4."""

import pytest

from agents.base import AgentDefinition
from agents.tools import AgentTools
from db import SessionLocal
from models.ollama_adapter import OllamaBackend
from orchestrator.executor import _build_memory_hook

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


def test_memory_hook_returns_empty_without_permission(db, backend: OllamaBackend) -> None:
    definition = AgentDefinition(agent_id="sin-permiso", rol="CTO", instrucciones="x", allowed_tools=[])
    tools = AgentTools(db=db, model_backend=backend, agent_id=definition.agent_id, allowed_tools=[])

    hook = _build_memory_hook(definition, tools, proyecto_id=None)
    assert hook.fetch_context is None  # sin permiso, no se conecta ninguna funcion real


def test_memory_hook_fetches_real_context_with_permission(db, backend: OllamaBackend) -> None:
    # Se simula que el hecho ya quedo guardado por un proceso de ingesta previo (ej. una
    # Conversacion anterior) - un ingestor con permiso propio de memory_store, distinto
    # del Agente bajo prueba, que solo tiene memory_search (principio de minimo privilegio).
    ingestor_tools = AgentTools(db=db, model_backend=backend, agent_id="ingestor", allowed_tools=["memory_store"])
    ingestor_tools.memory_store(
        "El cliente ya menciono antes que su problema es de flujo de caja.", origen="conversacion"
    )
    db.flush()

    definition = AgentDefinition(
        agent_id="diagnostico-nivel-1", rol="CEO", instrucciones="x", allowed_tools=["memory_search"]
    )
    tools = AgentTools(
        db=db, model_backend=backend, agent_id=definition.agent_id, allowed_tools=definition.allowed_tools
    )

    hook = _build_memory_hook(definition, tools, proyecto_id=None)
    assert hook.fetch_context is not None

    context = hook.fetch_context(definition.agent_id)
    assert "flujo de caja" in context.lower()
