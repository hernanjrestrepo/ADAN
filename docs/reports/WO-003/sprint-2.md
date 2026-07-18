# WO-003 Sprint 2 — Memoria semántica

**Célula:** C · **Fecha:** 2026-07-18

## Resumen ejecutivo

Pipeline de ingesta real: texto → chunking por párrafos (con overlap, sin dependencia de tokenizer todavía — Economía Conceptual) → embedding real por fragmento vía `OllamaBackend.embed()` (capa de Sprint 1 de WO-002, reutilizada sin duplicar) → persistencia en `memoria_semantica`. Búsqueda semántica real vía el operador nativo `cosine_distance` de pgvector — la similitud se calcula en Postgres, no en Python.

## Archivos creados

`ai/memory/chunking.py`, `ai/memory/ingestion.py`, `ai/memory/search.py`, `ai/tests/test_semantic_memory_functional.py`.

## Bugs encontrados

La FK real de `memoria_semantica.proyecto_id` → `proyectos.id` (mismo patrón que `kg_nodos` en Sprint 1) rompía la prueba de aislamiento por proyecto con UUIDs inventados — mismo bug, mismo tipo, ya conocido del Sprint anterior.

## Bugs corregidos

Reutilizado el helper `_create_real_proyecto()` de `test_kg_repository_functional.py` (duplicado deliberadamente en este archivo de prueba, no extraído a un módulo compartido todavía — dos usos no justifican una abstracción según la misma disciplina de Economía Conceptual que rige el resto del proyecto).

## Evidencias objetivas

- `ruff check .`: **All checks passed!**
- `pytest -v`: **3 passed** en 12.36s — chunking de texto corto/largo, ingesta real con embedding real de Ollama + búsqueda semántica real que encuentra el fragmento correcto por similitud (no por coincidencia de texto), y aislamiento por proyecto verificado con dos Proyectos reales.
- Suite completa de `/ai`: **18 passed** en 66.14s (todo lo acumulado de WO-002 + WO-003 hasta ahora).
- Verificado sin residuo en `memoria_semantica` ni `usuarios` tras la suite.

## Tiempo real (Wall Clock)

~25 minutos.

## Estado del Sprint

COMPLETO
