# WO-003 Sprint 1 — Esquema KG relacional

**Célula:** A · **Fecha:** 2026-07-18

## Resumen ejecutivo

Knowledge Graph relacional: `kg_nodos` (entidad/hecho/concepto, `proyecto_id` nullable — capa Global de AD-CMP-04 cuando es null), `kg_aristas` (relación dirigida), más `memoria_semantica` (preparada para Sprint 2, con columna `VECTOR(768)` real vía pgvector). No duplica las 37 entidades fijas de AD-005/006 — las complementa: el KG es la capa flexible para hechos y relaciones que un Agente descubre en conversación y que no encajan en una columna fija. Repositorio con CRUD + traversal BFS acotado en profundidad. API real en `/backend`: `POST /kg/nodes`, `POST /kg/edges`, `GET /kg/nodes/{id}`, `GET /kg/proyectos/{id}/nodes`, `GET /kg/nodes/{id}/traverse`.

## Archivos creados

`ai/memory/models.py`, `ai/memory/schema.sql`, `ai/memory/repository.py`, `ai/tests/test_kg_repository_functional.py`, `backend/app/models/kg.py` (espejo de lectura/escritura, mismo patrón que `ejecucion_agente.py`), `backend/app/routers/kg.py`, `backend/tests/test_kg_functional.py`.

## Archivos modificados

`ai/pyproject.toml` (dependencia `pgvector`, paquete `memory*`), `backend/app/main.py` (registra el router `/kg`).

## Bugs encontrados

1. **FK real de `kg_nodos.proyecto_id` → `proyectos.id` rompía las pruebas que usaban UUIDs aleatorios** como `proyecto_id` de prueba — correcto en producción (integridad referencial real), pero exigió que las pruebas de aislamiento por proyecto crearan un Usuario/Empresa/Proyecto real mínimo vía SQL crudo en vez de un UUID inventado.
2. **Residuo real en `kg_nodos`/`kg_aristas`** dejado por la prueba de API del backend (los endpoints hacen `commit()` real, correcto para producción, pero la prueba no limpiaba después).

## Bugs corregidos

1. Se agregó `_create_real_proyecto()` en las pruebas de `/ai` — crea filas mínimas reales vía SQL crudo, sin importar el ORM de `/backend` (misma disciplina de aislamiento del resto del proyecto).
2. La prueba de API del backend ahora borra explícitamente los nodos/aristas que crea al final.

## Evidencias objetivas

- `CREATE EXTENSION vector`, 3 tablas + 5 índices creados contra Postgres real (`docker exec ... psql < schema.sql`).
- `ai`: `ruff check .` limpio, **4 passed** (creación de nodo/arista, aislamiento por proyecto con Proyecto real, traversal BFS completo, traversal respeta `max_depth`).
- `backend`: `ruff check .` limpio, **10 passed** (8 heredados + 2 nuevos de la API del KG), verificado sin residuo tras limpieza.

## Tiempo real (Wall Clock)

~35 minutos.

## Estado del Sprint

COMPLETO
