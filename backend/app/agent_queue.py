"""Productor de tareas hacia la cola de /ai. Duplica intencionalmente el formato de mensaje
(no importa ai.orchestrator.queue - Plan Maestro SS3.2) siguiendo exactamente el contrato
de contracts/events/agent_execution.md. Cualquier cambio de formato debe actualizarse en
ambos lados y en ese documento, en el mismo commit."""

import json
import uuid

import redis

from app.config import get_settings

QUEUE_KEY = "adan:agent_runs:queue"


def get_redis_client() -> redis.Redis:
    settings = get_settings()
    return redis.from_url(settings.redis_url)


def enqueue_agent_run(agent_id: str, user_input: str, proyecto_id: str | None = None) -> str:
    execution_id = str(uuid.uuid4())
    message = {
        "execution_id": execution_id,
        "agent_id": agent_id,
        "user_input": user_input,
        "proyecto_id": proyecto_id,
    }
    client = get_redis_client()
    client.lpush(QUEUE_KEY, json.dumps(message))
    return execution_id
