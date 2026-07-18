# WO-002 Sprint 6 — Pruebas y documentación

**Célula:** C · **Fecha:** 2026-07-18

## Resumen ejecutivo

Prueba de carga ligera (5 ejecuciones concurrentes reales) verificada contra el worker real. Documentación de cómo definir un Agente nuevo (`ai/docs/COMO_DEFINIR_UN_AGENTE.md`). Verificación final completa de las tres suites (backend, ai, frontend E2E) tras encontrar y corregir una condición de carrera real entre las pruebas y el worker en ejecución continua.

## Archivos creados

`ai/tests/test_load_concurrent.py`, `ai/docs/COMO_DEFINIR_UN_AGENTE.md`.

## Archivos modificados

`ai/orchestrator/queue.py` (parámetro `queue_key` en `enqueue_run`/`dequeue_run`), `ai/tests/test_orchestrator_functional.py`, `backend/app/agent_queue.py`, `backend/tests/test_agents_functional.py`.

## Bugs encontrados

**Condición de carrera real entre las pruebas y el worker de desarrollo corriendo en segundo plano.** Con el worker de `/ai` activo (necesario para las pruebas manuales de Sprints 4-5), dos pruebas automatizadas que esperaban leer su propio mensaje de la cola Redis (`test_enqueue_and_dequeue_real_redis`, `test_run_known_agent_enqueues_real_redis_message`) empezaron a fallar de forma intermitente: el worker real, compitiendo por el mismo `BRPOP` (exclusivo — un mensaje solo lo recibe un consumidor), a veces se quedaba con el mensaje de la prueba antes de que la propia prueba lo leyera. No es un bug de producción — en CI no hay un worker persistente corriendo junto a la suite — pero sí un problema real de aislamiento de pruebas en desarrollo local, que además revela una propiedad correcta del sistema (la cola es realmente exclusiva, tal como debe ser).

## Bugs corregidos

Se parametrizó `queue_key` en ambos productores/consumidores (`ai/orchestrator/queue.py` y `backend/app/agent_queue.py`, este último leyendo el nombre de cola desde el módulo en tiempo de llamada, no como valor por defecto, para poder redirigirlo con `monkeypatch` sin tocar la API pública). Las dos pruebas afectadas ahora usan una clave de cola única por ejecución (`uuid4` en el nombre), aislándolas de cualquier worker real activo en la misma máquina.

## Evidencias objetivas

- **Prueba de carga:** 5 ejecuciones del Agente de Diagnóstico encoladas concurrentemente (`ThreadPoolExecutor`), procesadas por el worker real, verificadas una por una en Postgres real (ningún ID duplicado, ningún `user_input` mezclado entre tareas) — **1 passed en 17.06s**.
- **Backend:** `ruff check .` limpio, **8 passed**.
- **`/ai`:** `ruff check .` limpio, **11 passed** en 51.55s (incluye la prueba de carga).
- **Frontend:** `npm run lint` y `npm run build` limpios.
- **E2E completo contra el stack real en Docker:** **3 passed** (smoke de login/dashboard, flujo completo del Agente de Diagnóstico, protección de ruta privada).

## Tiempo real (Wall Clock)

~30 minutos (incluye 1 ciclo real de debugging de la condición de carrera).

## Estado del Sprint

COMPLETO
