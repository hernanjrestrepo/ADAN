"""Funcional: runtime de agentes contra Ollama real. BP-0007 (AD-006 SS4, entidad Agente)."""

import pytest

from agents.base import AgentDefinition, AgentRuntime, CancellationToken, MemoryHook, RunStatus
from models.ollama_adapter import OllamaBackend

pytestmark = pytest.mark.functional


@pytest.fixture
def runtime() -> AgentRuntime:
    return AgentRuntime(model_backend=OllamaBackend())


def test_agent_runs_to_completion(runtime: AgentRuntime) -> None:
    definition = AgentDefinition(
        agent_id="test-agent",
        rol="CTO",
        instrucciones="Responde de forma breve y directa.",
        max_steps=2,
    )
    result = runtime.run(definition, "Responde solo con: listo")

    assert result.status == RunStatus.COMPLETED
    assert result.final_output is not None
    assert len(result.steps) == 1  # un solo paso en esta version del runtime
    assert result.steps[0].call_record.model is not None
    assert result.error is None


def test_agent_respects_pre_cancellation(runtime: AgentRuntime) -> None:
    definition = AgentDefinition(agent_id="test-agent-2", rol="CTO", instrucciones="x")
    token = CancellationToken()
    token.cancel()

    result = runtime.run(definition, "esto no deberia ejecutarse", cancellation_token=token)

    assert result.status == RunStatus.CANCELLED
    assert len(result.steps) == 0


def test_agent_uses_memory_hooks(runtime: AgentRuntime) -> None:
    fetched_for: list[str] = []
    stored: list[tuple[str, str]] = []

    def fetch_context(agent_id: str) -> str:
        fetched_for.append(agent_id)
        return "La empresa se llama Paradixe Demo."

    def store_result(agent_id: str, output: str) -> None:
        stored.append((agent_id, output))

    runtime.memory_hook = MemoryHook(fetch_context=fetch_context, store_result=store_result)

    definition = AgentDefinition(agent_id="test-agent-3", rol="CEO", instrucciones="Se breve.")
    result = runtime.run(definition, "Cual es el contexto?")

    assert fetched_for == ["test-agent-3"]
    assert len(stored) == 1
    assert stored[0][0] == "test-agent-3"
    assert result.status == RunStatus.COMPLETED
