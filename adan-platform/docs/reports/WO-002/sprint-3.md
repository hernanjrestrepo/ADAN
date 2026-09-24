# WO-002 Sprint 3 — Orquestador

**Célula:** C · **Fecha:** 2026-07-18

## Resumen ejecutivo

Cola de tareas sobre Redis (`LPUSH`/`BRPOP`) + canal de eventos de progreso por ejecución (pub/sub). Tabla `ejecuciones_agente` (estado, transcript JSONB, tokens, timestamps) en el mismo Postgres físico que `/backend`, con FK real a `proyectos.id` a nivel de base de datos — sin que `/ai` importe el modelo ORM de `/backend` (Plan Maestro §3.2). Contrato de mensajes documentado en `contracts/events/agent_execution.md`. `execute_task` une runtime de agentes (Sprint 2) + persistencia + eventos. `worker.py` como entrypoint del proceso consumidor.

## Archivos creados

`ai/orchestrator/models.py`, `queue.py`, `executor.py`, `schema.sql`, `ai/worker.py`, `ai/agents/registry.py`, `contracts/events/agent_execution.md`, `ai/tests/test_orchestrator_functional.py`.

## Bugs encontrados

`Base.metadata.create_all()` (y luego cualquier `flush`/`commit` de un objeto `EjecucionAgente`) fallaba con `NoReferencedTableError`: al declarar `ForeignKey("proyectos.id")` en el modelo ORM de `/ai`, SQLAlchemy intenta resolver esa tabla dentro del `Base.metadata` **de `/ai`**, que deliberadamente no conoce el modelo `Proyecto` de `/backend` (aislamiento a propósito, Plan Maestro §3.2). No se detecta leyendo el código — solo al ejecutar un `create_all` o un `insert` real.

## Bugs corregidos

Se retiró `ForeignKey()` del lado Python del modelo — la restricción de integridad referencial real vive en Postgres (aplicada vía `schema.sql`, verificada con `\d ejecuciones_agente`), documentada explícitamente en el docstring del modelo para que nadie la reintroduzca sin entender por qué se quitó.

## Evidencias objetivas

- `docker exec adan-postgres-1 psql ... \d ejecuciones_agente`: tabla real con FK real a `proyectos(id)` verificada.
- `ruff check .`: **All checks passed!**
- `pytest -v` (contra Redis y Postgres reales): **10 passed** en 33.76s — incluye encolar/desencolar una tarea real, ejecutar un Agente completo con persistencia y verificar los eventos `started`/`completed` recibidos por un suscriptor real de Redis pub/sub.
- Verificado que la tabla queda vacía después de la suite (aislamiento real, sin residuo).

## Tiempo real (Wall Clock)

~35 minutos (incluye 1 ciclo real de debugging del bug de FK cruzada).

## Estado del Sprint

COMPLETO
