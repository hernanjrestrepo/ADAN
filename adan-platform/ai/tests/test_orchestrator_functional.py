"""Funcional: cola Redis + ejecucion + persistencia Postgres, contra infraestructura real."""

import uuid

import pytest

from agents.base import AgentDefinition, AgentRuntime
from agents.registry import register_agent
from db import SessionLocal
from models.ollama_adapter import OllamaBackend
from orchestrator.executor import execute_task
from orchestrator.models import EjecucionAgente
from orchestrator.queue import RunTask, dequeue_run, enqueue_run, get_redis_client, publish_event

pytestmark = pytest.mark.functional


@pytest.fixture(autouse=True)
def _register_test_agent():
    register_agent(
        AgentDefinition(
            agent_id="test-orchestrator-agent",
            rol="CTO",
            instrucciones="Responde de forma breve.",
        )
    )


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


def test_enqueue_and_dequeue_real_redis() -> None:
    # Cola aislada (no la real "adan:agent_runs:queue"): un worker real corriendo en la
    # misma maquina durante desarrollo consumiria este mensaje de prueba antes que el test
    # (BRPOP es exclusivo), dando un falso negativo. Ver docstring de enqueue_run/dequeue_run.
    test_queue_key = f"adan:agent_runs:test-queue:{uuid.uuid4().hex[:8]}"
    execution_id = enqueue_run(
        "test-orchestrator-agent", "hola mundo", queue_key=test_queue_key
    )
    assert execution_id is not None

    client = get_redis_client()
    task = dequeue_run(client, timeout_s=2, queue_key=test_queue_key)

    assert task is not None
    assert task.execution_id == execution_id
    assert task.agent_id == "test-orchestrator-agent"
    assert task.user_input == "hola mundo"


def test_execute_task_persists_and_publishes(db) -> None:
    execution_id = str(uuid.uuid4())
    task = RunTask(execution_id=execution_id, agent_id="test-orchestrator-agent", user_input="di listo")
    definition = AgentDefinition(agent_id="test-orchestrator-agent", rol="CTO", instrucciones="Se breve.")
    runtime = AgentRuntime(model_backend=OllamaBackend())

    client = get_redis_client()
    pubsub = client.pubsub()
    pubsub.subscribe(f"adan:agent_runs:{execution_id}:events")
    pubsub.get_message(timeout=1)  # consume el mensaje de confirmacion de suscripcion

    ejecucion = execute_task(task, definition, runtime, db)
    db.commit()

    assert ejecucion.status == "completed"
    assert ejecucion.final_output is not None

    fetched = db.query(EjecucionAgente).filter(EjecucionAgente.id == ejecucion.id).first()
    assert fetched is not None
    assert fetched.transcript is not None
    assert len(fetched.transcript) == 1

    events = []
    for _ in range(5):
        msg = pubsub.get_message(timeout=2)
        if msg and msg["type"] == "message":
            events.append(msg["data"])
    assert len(events) >= 2  # started + completed

    db.delete(fetched)
    db.commit()


def test_publish_event_reaches_subscriber() -> None:
    client = get_redis_client()
    execution_id = str(uuid.uuid4())
    pubsub = client.pubsub()
    pubsub.subscribe(f"adan:agent_runs:{execution_id}:events")
    pubsub.get_message(timeout=1)

    publish_event(client, execution_id, "started", {"agent_id": "x"})

    msg = pubsub.get_message(timeout=2)
    assert msg is not None
    assert msg["type"] == "message"
