# WO-003 Sprint 3 — Consulta híbrida

**Célula:** A/C · **Fecha:** 2026-07-18

## Resumen ejecutivo

Consulta híbrida real: búsqueda semántica (pgvector `cosine_distance`) + traversal del grafo desde los mejores resultados semánticos, combinados en un solo ranking. Razón de ser: dos hechos pueden estar conectados en el grafo sin parecerse semánticamente — un traversal desde los hits semánticos rescata ese contexto relacionado que la búsqueda por embedding, sola, no vería. Implementado tanto en `/ai` (`memory/hybrid_query.py`, para el futuro tool-calling de Agentes) como en `/backend` (`GET /kg/query`, para la API pública) — deliberadamente reimplementado, no importado, siguiendo el mismo patrón de aislamiento de todo el proyecto. Contrato OpenAPI **exportado real** desde la app FastAPI viva (`contracts/openapi/schema.json`), no escrito a mano.

## Archivos creados

`ai/memory/hybrid_query.py`, `ai/tests/test_hybrid_query_functional.py`, `backend/app/embeddings.py` (cliente mínimo de embeddings, llama a Ollama directo sin importar `ai.models`), `backend/tests/test_hybrid_query_functional.py`, `contracts/openapi/schema.json`.

## Archivos modificados

`backend/app/models/kg.py` (`MemoriaSemanticaBackend`, espejo con columna `Vector(768)`), `backend/app/routers/kg.py` (`GET /kg/query`, más `_traverse_from()` extraído como helper reutilizable dentro del propio router).

## Bugs encontrados

**Orden de borrado no determinista en la limpieza de una prueba.** El primer intento de limpiar los datos de prueba usó `db.delete()` sobre objetos ORM (nodo, arista, memoria) — pero como `KGAristaBackend`/`MemoriaSemanticaBackend` no declaran `ForeignKey()`/`relationship()` hacia `KGNodoBackend` (a propósito, para no acoplar metadata entre módulos), SQLAlchemy no tiene forma de saber que las aristas deben borrarse antes que los nodos, y el orden de `flush()` que eligió violó la FK real de Postgres.

## Bugs corregidos

Se reemplazó el borrado por objetos ORM por `DELETE` crudo (`text()`) en el orden explícito correcto (memoria y aristas antes que nodos) — mismo patrón ya usado en `test_kg_functional.py`. Se verificó ejecutando la prueba de nuevo y confirmando `count(*) = 0` en las tres tablas afectadas.

## Evidencias objetivas

- `ai`: `ruff check .` limpio, **1 passed** — el hecho conectado por grafo ("se buscó un proveedor alternativo...") aparece en los resultados aunque su texto no se parece al query, y rankea después del resultado semántico directo (distancia mayor, tal como se diseñó).
- `backend`: `ruff check .` limpio, **11 passed** (suite completa, incluida la nueva prueba de `GET /kg/query` contra la API HTTP real).
- `contracts/openapi/schema.json`: exportado desde `app.openapi()` de la aplicación real en ejecución — refleja los endpoints reales, no una copia mantenida a mano que pueda desincronizarse.
- Verificado sin residuo en `kg_nodos`, `kg_aristas`, `memoria_semantica` tras la corrección.

## Tiempo real (Wall Clock)

~40 minutos (incluye 1 ciclo real de debugging del orden de borrado).

## Estado del Sprint

COMPLETO
