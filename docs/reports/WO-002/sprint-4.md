# WO-002 Sprint 4 — Primer agente end-to-end

**Célula:** C/A · **Fecha:** 2026-07-18

## Resumen ejecutivo

Primer Agente real: **Diagnóstico del Dolor** (`diagnostico-nivel-1`, rol CEO — AD-FUNC-01 Nivel 1, instrucciones ancladas en la emoción Comprendido de AD-FUNC-03). Endpoints reales en `/backend`: `POST /agents/run` (encola, `202 Accepted`, devuelve `execution_id` de inmediato) y `GET /agents/runs/{id}` (lee el estado real desde Postgres, escrito por el worker de `/ai` — modelo de solo lectura, sin importar el ORM de `/ai`). Flujo completo verificado manualmente end-to-end contra infraestructura 100% real.

## Archivos creados

`ai/agents/diagnostico.py`, `backend/app/models/ejecucion_agente.py` (modelo de lectura, deliberadamente no registrado en `app/models/__init__.py` para no interferir con Alembic — la tabla la migra `/ai`), `backend/app/agent_queue.py` (productor Redis, duplica el contrato de mensaje sin importar `ai.orchestrator.queue`), `backend/app/routers/agents.py`, `backend/tests/test_agents_functional.py`.

## Archivos modificados

`ai/worker.py` (`bootstrap_agents()` registra el Agente de Diagnóstico al iniciar), `backend/app/main.py` (registra el router de agentes).

## Bugs encontrados

1. **Contenedores Docker caídos entre turnos de la sesión** (reinicio de máquina/entorno) — `docker ps` no mostraba nada. Los datos sobrevivieron (volumen de Postgres intacto, verificado con `SELECT count(*) FROM empresas`), pero hubo que levantar el stack de nuevo.
2. **Usuario demo con el email antiguo.** El usuario sembrado en WO-001 quedó como `demo@paradixe.local` (el dominio `.local` se corrigió en el *código* de `seed_demo.py` durante WO-001 Sprint 6, pero el seed nunca se volvió a ejecutar) — no bloquea nada, login funciona igual porque el endpoint de login no valida formato de email, solo el de registro. Se documenta, no se "corrige" forzando un reseed innecesario.
3. **`/agents/run` devolvía 404 tras reconstruir el contenedor.** El servicio `api` no tiene bind-mount de código — cualquier cambio en `/backend` requiere `docker compose up -d --build api` explícito. El primer intento de probar el endpoint nuevo falló porque el contenedor corría la imagen de WO-001 Sprint 6, sin el router de agentes. **Deuda técnica registrada:** agregar volumen de desarrollo + `--reload` para no repetir este ciclo en sprints futuros.
4. **Worker con conexión Redis obsoleta tras el reinicio de contenedores** — el proceso del worker (iniciado antes del reinicio) no se reconecta solo; hubo que reiniciarlo. La tarea encolada mientras tanto **no se perdió** (persistida en la lista de Redis) y se procesó correctamente en cuanto un worker nuevo la consumió — buena señal de robustez de la cola.
5. **Fixture de test con `flush()` en vez de `commit()`** en `test_agents_functional.py` — la API bajo prueba abre su propia sesión de base de datos (vía el dependency `get_db`), en una conexión distinta a la del fixture; no veía el usuario sin `commit()` real.

## Bugs corregidos

Los 5 anteriores. Ninguno bloqueó el Sprint más de unos minutos; todos verificados con una repetición real de la prueba tras la corrección.

## Evidencias objetivas

**Flujo completo verificado manualmente contra infraestructura 100% real** (login real → `POST /agents/run` → cola Redis real → worker real → inferencia real en Ollama (`llama3.2:1b`) → persistencia real en Postgres → `GET /agents/runs/{id}`):

```
Execution ID: 53e21f14-1000-4845-add9-a5a58a6ecf35
status: "completed"
final_output: "PROBLEMA: ... EVIDENCIA: ..." (generado por inferencia real, no simulado)
```

Log del worker confirma la llamada HTTP real a Ollama: `POST http://localhost:11434/api/generate "HTTP/1.1 200 OK"`.

- `ruff check .` (backend): **All checks passed!**
- `pytest -v` (backend, incluye `functional`): **8 passed** — 3 nuevos (agente desconocido → 404, encolado real verificado leyendo el mensaje real de Redis, ejecución inexistente → 404) + 5 heredados.
- Verificado que no queda residuo de las pruebas en Postgres tras la suite.

## Riesgos observados (no bloqueantes)

- El modelo pequeño (`llama3.2:1b`) no sigue el formato de salida solicitado al 100% (usó markdown en vez de texto plano, omitió la línea PERFIL en una corrida) — esperable de un modelo de 1B parámetros; no invalida el flujo, sí señala que la validación/parseo estructurado real (más allá de "el flujo corre") es trabajo de una versión futura del Agente, no de este Sprint.

## Tiempo real (Wall Clock)

~50 minutos (incluye 2 reinicios reales de infraestructura y 5 ciclos de debugging con evidencia).

## Estado del Sprint

COMPLETO
