"""Entrypoint del worker de /ai: consume tareas de Redis, ejecuta el Agente correspondiente,
persiste el resultado. Uso: python worker.py (dentro del venv de /ai).

El registro de Agentes disponibles vive en agents/registry.py. bootstrap_agents() registra
aqui, al arrancar el proceso, todos los Agentes reales conocidos (Sprint 4 agrega el
primero: Diagnostico del Dolor). Agentes desconocidos se marcan failed con mensaje explicito."""

import logging
import time

from agents.base import AgentRuntime
from agents.diagnostico import build_diagnostico_agent
from agents.registry import get_agent_definition, register_agent
from db import SessionLocal
from models.ollama_adapter import OllamaBackend
from orchestrator.executor import execute_task
from orchestrator.queue import dequeue_run, get_redis_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("adan.ai.worker")


def bootstrap_agents() -> None:
    """Registra todos los Agentes reales conocidos por el sistema. Se llama una vez al
    iniciar el worker (y en los tests que necesiten resolver estos agent_id)."""
    register_agent(build_diagnostico_agent())


def main() -> None:
    bootstrap_agents()
    redis_client = get_redis_client()
    runtime = AgentRuntime(model_backend=OllamaBackend())
    logger.info("Worker started, waiting for tasks on the queue...")

    while True:
        task = dequeue_run(redis_client, timeout_s=5)
        if task is None:
            continue

        definition = get_agent_definition(task.agent_id)
        if definition is None:
            logger.error("Unknown agent_id=%s, skipping task %s", task.agent_id, task.execution_id)
            continue

        db = SessionLocal()
        try:
            execute_task(task, definition, runtime, db)
        finally:
            db.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        time.sleep(0.1)
        logger.info("Worker stopped.")
