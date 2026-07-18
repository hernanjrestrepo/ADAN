# Convenciones — ADÁN Platform

Rige la Metodología Paradixe – Work Order Execution v2, con las Enmiendas 1 y 2 del Plan Maestro de Ejecución ADÁN v1.0. Este documento fija solo lo operativo del día a día.

## Idiomas

- Código, commits, identificadores (variables, clases, funciones, tablas): **inglés**.
- Documentación, reportes, ADRs, mensajes de usuario final: **español**.

## Estructura del monorepo

```
/backend    → Célula A. FastAPI + SQLAlchemy 2 + Alembic. Python 3.12.
/frontend   → Célula B. React 18 + Vite + Tailwind. Playwright para E2E.
/ai         → Célula C. Runtime de agentes propio (prohibido LangChain/LangGraph/CrewAI).
/contracts  → Frontera entre células. OpenAPI (/contracts/openapi), eventos (/contracts/events).
/docs       → Célula D. Blueprint, ADRs, reportes, bloqueos.
/infra      → Docker Compose, scripts de infraestructura.
/scripts    → Utilidades de desarrollo (seed, migraciones, setup).
```

## Ownership

`/backend` → A · `/frontend` → B · `/ai` → C · `/docs`, `/contracts` (aprueba), `/adr` → D.
Cambios cruzados requieren PR etiquetado a la célula dueña; si no responde en el mismo sprint, la Célula D arbitra.

## Git

- Monorepo único, trunk-based. Ramas cortas por sprint: `wo-XXX/sprint-N-descripcion`.
- Merge a `main` al cerrar cada sprint. Prohibido acumular sprints sin versionar.
- Un commit mínimo por sprint, mensaje descriptivo, evidencia asociada.
- Cierre de WO exige: repo limpio, baseline reproducible, commit final + tag `wo-XXX-done`.

## Trazabilidad

Todo modelo/endpoint/componente que implemente un requisito del blueprint referencia su `BP-####` (ver `docs/blueprint/TRACEABILITY.md`) en su docstring o comentario de cabecera.

## Reutilización

Auditar antes de escribir. Activos autorizados como cantera (ADR-R): EVA, JobXeeker, NOURA, TradeHub, MigPAL, VDC, infraestructura FastAPI/Ollama/auth/analytics/observabilidad/React/Docker ya existente en el ecosistema Paradixe.

## Evidencia objetiva

Nunca "debería funcionar". Pruebas contra infraestructura real (Ollama, FastAPI, PostgreSQL, Redis, navegador, Docker). La inspección de código no es evidencia. No repetir pruebas ya aprobadas si el código no cambió.

## Las cuatro paradas duras

1. Dinero real (APIs de pago, servicios cloud de pago, compras).
2. Credenciales que no existen en el entorno.
3. Información externa inexistente y no derivable.
4. Riesgo real de pérdida de información sin respaldo verificado.

Ver `docs/blocks/BLOCKS.md` para el protocolo completo.
