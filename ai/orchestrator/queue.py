"""Cola de tareas sobre Redis + canal de eventos de progreso. Contrato de mensaje
documentado en contracts/events/agent_execution.md - cualquier productor (backend) o
consumidor (worker de /ai) debe respetar ese formato exacto."""

import json
import uuid
from dataclasses import asdict, dataclass

import redis

from config import get_ai_settings

QUEUE_KEY = "adan:agent_runs:queue"


def _events_channel(execution_id: str) -> str:
    return f"adan:agent_runs:{execution_id}:events"


@dataclass
class RunTask:
    execution_id: str
    agent_id: str
    user_input: str
    proyecto_id: str | None = None


def get_redis_client() -> redis.Redis:
    settings = get_ai_settings()
    return redis.from_url(settings.redis_url)


def enqueue_run(agent_id: str, user_input: str, proyecto_id: str | None = None) -> str:
    """Encola una ejecucion. Devuelve el execution_id para que el llamador (backend)
    pueda hacer seguimiento via Postgres o suscribirse al canal de eventos."""
    execution_id = str(uuid.uuid4())
    task = RunTask(execution_id=execution_id, agent_id=agent_id, user_input=user_input, proyecto_id=proyecto_id)
    client = get_redis_client()
    client.lpush(QUEUE_KEY, json.dumps(asdict(task)))
    return execution_id


def dequeue_run(client: redis.Redis, timeout_s: int = 5) -> RunTask | None:
    """Bloqueante hasta timeout_s. Usado por el worker."""
    result = client.brpop([QUEUE_KEY], timeout=timeout_s)
    if result is None:
        return None
    _, raw = result
    data = json.loads(raw)
    return RunTask(**data)


def publish_event(client: redis.Redis, execution_id: str, event_type: str, payload: dict) -> None:
    message = json.dumps({"type": event_type, "payload": payload})
    client.publish(_events_channel(execution_id), message)


def subscribe_events(client: redis.Redis, execution_id: str):
    pubsub = client.pubsub()
    pubsub.subscribe(_events_channel(execution_id))
    return pubsub
