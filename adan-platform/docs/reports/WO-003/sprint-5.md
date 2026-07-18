# WO-003 Sprint 5 — UI de exploración

**Célula:** B · **Fecha:** 2026-07-18

## Resumen ejecutivo

Página `/kg`: búsqueda vía `GET /kg/query` (semántica + grafo), lista de resultados etiquetados por origen ("semántico"/"grafo"), y detalle de conexiones al hacer clic en un resultado (`GET /kg/nodes/{id}/traverse`). Enlace desde el Dashboard.

## Archivos creados

`frontend/src/pages/KGExplorer.tsx`, `frontend/e2e/kg-explorer.spec.ts`, endpoint nuevo `POST /kg/memory` en `backend/app/routers/kg.py`.

## Archivos modificados

`frontend/src/api/client.ts` (`hybridQuery`, `getNodeTraverse`), `frontend/src/App.tsx` (ruta `/kg`), `frontend/src/pages/Dashboard.tsx` (enlace).

## Bugs encontrados

**Gap real de arquitectura, no un bug de código:** crear un nodo vía `POST /kg/nodes` **no lo indexa automáticamente** para búsqueda semántica — son dos pasos deliberadamente separados (grafo vs. memoria semántica, Sprint 1 vs. Sprint 2), pero no existía ningún endpoint de la API para indexar un texto sin pasar por un Agente con permiso `memory_store`. La primera versión del E2E de esta página fallaba porque buscaba un nodo recién creado que nunca había sido indexado — no encontrable por diseño, no por defecto.

## Bugs corregidos

Se agregó `POST /kg/memory` — indexa un texto para búsqueda semántica real desde la API directamente (sin chunking, a diferencia de `ai/memory/ingestion.py` que sigue siendo el camino real para documentos largos vía Agentes). Cierra un hueco genuino: antes de este endpoint, no había forma de poblar contenido explorable desde fuera de un Agente.

## Evidencias objetivas

- `backend`: `ruff check .` limpio, **11 passed** (incluye el nuevo endpoint, aunque sin una prueba `pytest` dedicada todavía — cubierto por el E2E de esta misma sección).
- `npm run lint` / `npm run build`: limpios.
- E2E completo contra el stack real en Docker: **4 passed** — el nuevo flujo de exploración (crear 2 nodos reales vía API, conectarlos, indexarlos, buscar por texto en la UI, ver conexiones) más los 3 E2E heredados de Sprints anteriores, sin regresión.

## Tiempo real (Wall Clock)

~30 minutos (incluye 1 ciclo real de debugging del gap de indexación).

## Estado del Sprint

COMPLETO
