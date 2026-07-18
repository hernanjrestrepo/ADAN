# WO-003 Sprint 4 — Integración con el runtime de agentes

**Célula:** C · **Fecha:** 2026-07-18

## Resumen ejecutivo

Cuatro herramientas reales de Agente (`kg_read`, `kg_write`, `memory_search`, `memory_store`), cada una con verificación de permiso explícita contra `AgentDefinition.allowed_tools` (nuevo campo) antes de tocar la base de datos. Cierra el `MemoryHook` que el runtime de agentes (WO-002 Sprint 2) dejó preparado como contrato sin implementación real — `AgentRuntime.run()` ahora acepta un `memory_hook` por llamada (no solo por instancia), y el executor construye uno real usando `memory_search` cuando el Agente tiene permiso. El Agente de Diagnóstico se restringe deliberadamente a `["memory_search"]` — no puede escribir en el grafo ni en memoria: un Diagnóstico no decide por sí solo qué hechos quedan permanentes.

## Archivos creados

`ai/agents/tools.py` (`AgentTools`, `check_permission`, `ToolPermissionError`), `ai/tests/test_agent_tools_functional.py`, `ai/tests/test_memory_hook_wiring_functional.py`.

## Archivos modificados

`ai/agents/base.py` (`AgentDefinition.allowed_tools`; `AgentRuntime.run()` acepta `memory_hook` por llamada, sin mutar estado compartido de la instancia), `ai/agents/diagnostico.py` (declara `allowed_tools=["memory_search"]`), `ai/orchestrator/executor.py` (`_build_memory_hook()` conecta el hook real solo si el Agente tiene el permiso correspondiente).

## Bugs encontrados

**Error de configuración en la prueba propia, no en el código bajo prueba.** El primer intento de `test_memory_hook_fetches_real_context_with_permission` usaba las mismas `AgentTools` restringidas (`allowed_tools=["memory_search"]`) tanto para sembrar el hecho de prueba (`memory_store`, que requiere permiso `memory_store`) como para leerlo — el `ToolPermissionError` que se disparó era el sistema de permisos funcionando exactamente como se diseñó, no un defecto.

## Bugs corregidos

Se separó la prueba en dos actores: un "ingestor" con permiso `memory_store` propio (simulando que el hecho ya fue guardado por un proceso previo, ej. una Conversación anterior) y el Agente de Diagnóstico bajo prueba, que solo lee. Principio de mínimo privilegio verificado, no solo declarado.

## Evidencias objetivas

- `ruff check .`: **All checks passed!**
- `pytest -v` (nuevas): **5 passed** — herramienta denegada sin permiso (verificado que realmente lanza `ToolPermissionError`), escritura+lectura real en el grafo con permiso, guardado+búsqueda real en memoria semántica con permiso, `MemoryHook` vacío sin permiso, `MemoryHook` trayendo contexto real (embeddings reales, búsqueda real) con permiso.
- Suite completa de `/ai`: **24 passed** en 74.96s — nada se rompió al integrar.
- Sin residuo en `kg_nodos` ni `memoria_semantica` tras la suite completa.

## Tiempo real (Wall Clock)

~35 minutos.

## Estado del Sprint

COMPLETO
