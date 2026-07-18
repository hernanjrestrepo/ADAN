"""Une runtime de agentes + persistencia Postgres + eventos Redis. Es lo que corre el
worker (ver worker.py) por cada tarea que saca de la cola."""

import logging
import uuid

from sqlalchemy.orm import Session

from agents.base import AgentDefinition, AgentRuntime, RunStatus
from orchestrator.models import EjecucionAgente
from orchestrator.queue import RunTask, get_redis_client, publish_event

logger = logging.getLogger("adan.ai.executor")


def execute_task(
    task: RunTask,
    definition: AgentDefinition,
    runtime: AgentRuntime,
    db: Session,
) -> EjecucionAgente:
    redis_client = get_redis_client()

    ejecucion = EjecucionAgente(
        id=uuid.UUID(task.execution_id),
        agent_id=task.agent_id,
        proyecto_id=uuid.UUID(task.proyecto_id) if task.proyecto_id else None,
        status=RunStatus.RUNNING.value,
        user_input=task.user_input,
    )
    db.add(ejecucion)
    db.commit()
    publish_event(redis_client, task.execution_id, "started", {"agent_id": task.agent_id})

    result = runtime.run(definition, task.user_input)

    ejecucion.status = result.status.value
    ejecucion.final_output = result.final_output
    ejecucion.error = result.error
    ejecucion.finished_at = result.finished_at
    ejecucion.transcript = [
        {
            "step_number": s.step_number,
            "prompt": s.prompt,
            "output": s.output,
        }
        for s in result.steps
    ]
    if result.steps:
        last_record = result.steps[-1].call_record
        ejecucion.prompt_tokens = getattr(last_record, "prompt_tokens", None)
        ejecucion.completion_tokens = getattr(last_record, "completion_tokens", None)

    db.commit()

    publish_event(
        redis_client,
        task.execution_id,
        "completed" if result.status == RunStatus.COMPLETED else result.status.value,
        {"final_output": result.final_output, "error": result.error},
    )
    logger.info("Execution %s finished with status=%s", task.execution_id, result.status)
    return ejecucion
