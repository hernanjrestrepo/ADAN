# Cierre de WO-002 — Núcleo de Agentes y Orquestador

**Líder:** C · **Apoyo:** A, B · **Fecha de cierre:** 2026-07-18 · **Tag:** `wo-002-done`

## Resultado consolidado

Runtime de agentes propio y funcionando end-to-end, sin frameworks de terceros. Capa de abstracción de modelos (`ModelBackend`) con adaptador Ollama real (reintentos, timeouts, streaming, embeddings, salida estructurada). Runtime de agentes con ciclo de vida completo, cancelación cooperativa y hooks de memoria (implementación real diferida a WO-003). Orquestador con cola Redis + tabla de ejecuciones en Postgres, sin acoplamiento de import entre `/backend` y `/ai` (contrato documentado en `contracts/events/agent_execution.md`). Primer Agente real (Diagnóstico del Dolor, Nivel 1) corriendo de punta a punta: UI → API → cola → worker → Ollama real → Postgres → UI, con progreso por polling e historial.

## Evidencias

- 6 sprints, 6 commits, tag `wo-002-done`.
- 4 tests reales contra Ollama (generación, streaming, embeddings, salida estructurada).
- 7 tests del runtime de agentes y orquestador contra Redis+Postgres reales.
- 1 prueba de carga (5 ejecuciones concurrentes) verificada sin pérdida ni corrupción de datos.
- 8 tests del backend (incluye el endpoint `/agents/*`).
- 3 E2E Playwright contra el stack completo en Docker, incluido el flujo real del Agente de Diagnóstico con inferencia real.
- **7 bugs reales encontrados y corregidos durante la verificación end-to-end** a lo largo de la WO (ninguno detectable solo leyendo código): contenedores caídos entre turnos de sesión (datos sobrevivieron vía volumen), usuario demo con email desactualizado, contenedor `api` sin rebuild tras cambios de código, worker con conexión Redis obsoleta tras reinicio, `TimeoutError` de socket sin capturar matando el worker, selector de Playwright ambiguo con el historial, condición de carrera entre pruebas y el worker de desarrollo.

## Riesgos abiertos

- El progreso de ejecución es por *polling* (1.5s), no *streaming* token-a-token — decisión de diseño explícita, se revisará cuando el Board Room (WO-005) necesite ver deliberación multiagente en tiempo real.
- `AgentRuntime` ejecuta un solo paso de inferencia por corrida — sin bucle de tool-calling todavía (herramientas reales llegan con el Knowledge Graph de WO-003).
- El modelo pequeño de desarrollo (`llama3.2:1b`) no sigue el formato de salida solicitado al 100% — esperable de un modelo de 1B parámetros, no invalida el flujo.

## Deuda técnica

- **Sin hot-reload en desarrollo** para `/backend` y `/frontend` en Docker — cada cambio de código requiere `docker compose up -d --build`. Registrado explícitamente para atender en un futuro sprint de developer experience (no bloqueante, pero ralentizó la verificación de esta WO).
- Sin refresh tokens ni rate limiting de login (heredado de WO-001, ADR-002).

## Dependencias externas

Ninguna nueva. Ollama del host (ADR-001) sigue siendo la única dependencia externa real, ya resuelta.

## Recomendación siguiente WO

Continuar con **WO-003 (Memoria + Knowledge Graph)**, tal como fija la cadena. Es, además, la pieza que resuelve el `MemoryHook` que el runtime de agentes dejó preparado desde Sprint 2 sin implementación real. Ninguna desviación propuesta.
