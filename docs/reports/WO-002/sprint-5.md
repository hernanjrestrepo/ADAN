# WO-002 Sprint 5 — UI mínima de agentes

**Célula:** B · **Fecha:** 2026-07-18

## Resumen ejecutivo

Página `/agents`: formulario para lanzar el Agente de Diagnóstico, panel de "ejecución en curso" con **progreso por polling** (cada 1.5s contra `GET /agents/runs/{id}` hasta `completed`/`failed`/`cancelled` — decisión de diseño explícita, no streaming token-a-token; ver Riesgos), historial de ejecuciones (`GET /agents/runs`, más reciente primero). Enlace desde el Dashboard.

## Archivos creados

`frontend/src/pages/Agents.tsx`, `frontend/e2e/agents.spec.ts`.

## Archivos modificados

`frontend/src/api/client.ts` (runAgent/getRun/listRuns), `frontend/src/App.tsx` (ruta `/agents`), `frontend/src/pages/Dashboard.tsx` (enlace), `backend/app/routers/agents.py` (nuevo `GET /agents/runs` con límite), `ai/orchestrator/queue.py` y `ai/worker.py` (bug real, ver abajo).

## Bugs encontrados

1. **El worker moría por un `TimeoutError` de socket sin capturar.** `redis-py`, en este entorno, propaga `redis.exceptions.TimeoutError` cuando `BRPOP` agota su timeout de bloqueo sin mensajes — en vez de devolver `None` como se esperaba. El worker llevaba minutos muriendo silenciosamente entre pruebas manuales sin que se notara hasta que dejó de recoger tareas.
2. **Selector de Playwright ambiguo.** `getByText(/^completed$/)` sin escopar resolvía dos veces (panel de ejecución en curso + historial) — y peor, en una segunda vuelta, coincidía con ejecuciones **previas** ya completadas del historial (de pruebas manuales de Sprint 4), dando un falso positivo antes de que la ejecución real de esta prueba terminara.

## Bugs corregidos

1. `dequeue_run` ahora captura `redis.exceptions.TimeoutError` y lo normaliza a `None` (es "no hay tarea todavía", no un error). Se añadió además una captura general en el loop principal del worker para que ninguna excepción individual mate el proceso completo.
2. Se agregó `data-testid="current-execution"` al panel real de ejecución en curso; el test ahora escopa sus aserciones dentro de ese contenedor, no en toda la página.

## Evidencias objetivas

- `npm run lint` / `npm run build`: limpios.
- Worker reiniciado con el fix: **sigue vivo pasados 20+ segundos** sin tareas en la cola (antes moría casi de inmediato).
- Playwright contra el stack completo en Docker: **3 passed** — el smoke original de login/dashboard, la nueva prueba de lanzar el Agente de Diagnóstico end-to-end (registro → login → clic en "Agente de Diagnóstico" → escribir problema → esperar `completed` real → verificar que el `<pre>` del resultado no está vacío), y la protección de ruta privada.

## Tiempo real (Wall Clock)

~40 minutos (incluye 1 ciclo real de debugging del worker y 2 iteraciones sobre el selector de Playwright).

## Estado del Sprint

COMPLETO — nota de alcance: el progreso es por *polling*, no *streaming* real (token-a-token vía WebSocket/SSE). Se documenta como Decisión de Diseño diferida, no como omisión — se revisará cuando el Board Room (WO-005) necesite ver la deliberación multiagente en tiempo real, donde el streaming sí aporta valor claro.
