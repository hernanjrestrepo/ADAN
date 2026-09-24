# Cierre de WO-003 — Memoria + Knowledge Graph

**Líder:** A · **Apoyo:** C, B · **Fecha de cierre:** 2026-07-18 · **Tag:** `wo-003-done`

## Resultado consolidado

Knowledge Graph relacional (`kg_nodos`/`kg_aristas`, complementa sin duplicar las 37 entidades fijas del blueprint) y memoria semántica real (pgvector + embeddings reales de Ollama) operativas y usadas por los agentes. Consulta híbrida (semántica + traversal de grafo) demostrada con un corpus de negocio realista — rescata hechos causalmente conectados que la búsqueda semántica sola no encontraría. Herramientas reales de Agente (`kg_read`, `kg_write`, `memory_search`, `memory_store`) con permisos explícitos por Agente, cerrando el `MemoryHook` que WO-002 había dejado como contrato sin implementación. UI de exploración funcional.

## Evidencias

- 6 sprints, 6 commits.
- 24 tests en `/ai` (Ollama real, Postgres real, Redis real), 11 en `/backend`, 4 E2E Playwright contra el stack completo en Docker.
- Corpus demo real con resultado documentado: consulta híbrida rescatando una decisión de junta directiva causalmente conectada a una cadena de hechos, sin mención textual directa — la prueba más concreta de que la arquitectura híbrida (no solo semántica) aporta valor real.
- **4 bugs reales encontrados y corregidos**, todos solo visibles ejecutando contra infraestructura real: FK reales rotas por pruebas con UUIDs inventados (dos veces, mismo patrón — ya anticipado la segunda vez), orden de borrado no determinista entre modelos espejo sin `relationship()` declarada, error de configuración de prueba que en realidad confirmó que el sistema de permisos funciona correctamente, y un gap arquitectónico real (crear un nodo no lo indexa automáticamente para búsqueda semántica) resuelto con un endpoint nuevo (`POST /kg/memory`).

## Riesgos abiertos

- El índice HNSW de pgvector para búsqueda aproximada no se creó — con el volumen actual (corpus demo pequeño), un scan exacto es suficiente y más simple; se revisará con evidencia real de volumen, no antes.
- `AgentTools.kg_write`/`memory_store` no tienen todavía un caso de uso real que las invoque desde un Agente (solo el Diagnóstico existe, y está restringido a solo lectura) — la infraestructura de permisos está lista, falta un Agente que realmente necesite escribir.

## Deuda técnica

- Heredada de WO-002: sin hot-reload en desarrollo para `/backend`/`/frontend`.
- Lógica de consulta híbrida duplicada entre `/ai` (`memory/hybrid_query.py`) y `/backend` (`routers/kg.py`) — deliberado (Plan Maestro §3.2), pero registrado como superficie a vigilar si diverge con el tiempo.

## Dependencias externas

Ninguna nueva.

## Recomendación siguiente WO

Continuar con **WO-004 (Gemelo Digital v1)**, tal como fija la cadena — el motor de eventos y snapshots que necesita puede apoyarse directamente en el Knowledge Graph y la memoria semántica ya construidos. Ninguna desviación propuesta.
