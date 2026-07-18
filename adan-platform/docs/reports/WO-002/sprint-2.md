# WO-002 Sprint 2 — Runtime de agentes

**Célula:** C · **Fecha:** 2026-07-18

## Resumen ejecutivo

`AgentDefinition` declarativa (rol, instrucciones, herramientas, límites de pasos/tokens — AD-003 entidad Agente). `AgentRuntime` ejecuta una definición contra un input real, con cancelación cooperativa (`CancellationToken`, revisada entre pasos, nunca interrumpe una llamada de inferencia en curso), ciclo de vida (`RunStatus`: pending/running/completed/failed/cancelled), y `MemoryHook` — punto de enganche a la jerarquía de 5 capas de AD-CMP-04, con implementación real diferida a WO-003 (Knowledge Graph/memoria semántica) para no reescribir el runtime después. Sin frameworks de terceros (LangChain/LangGraph/CrewAI), como exige el Plan Maestro.

## Archivos creados

`ai/agents/base.py`, `ai/tests/test_agent_runtime.py`.

## Bugs encontrados

Ruff (`UP042`) — `RunStatus(str, Enum)` es el patrón antiguo; Python 3.12 ya soporta `StrEnum` directamente.

## Bugs corregidos

Cambiado a `class RunStatus(StrEnum)`.

## Evidencias objetivas

- `ruff check .`: **All checks passed!**
- `pytest -v` (marcado `functional`, contra Ollama real): **7 passed** en 22.38s — incluye ejecución completa de un Agente con inferencia real, cancelación pre-ejecución (cero pasos consumidos), y hooks de memoria (fetch/store) verificados con espías reales, no mocks de librería.

## Tiempo real (Wall Clock)

~20 minutos.

## Estado del Sprint

COMPLETO
