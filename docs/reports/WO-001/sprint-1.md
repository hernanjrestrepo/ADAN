# WO-001 Sprint 1 — Monorepo y tooling

**Célula:** A · **Fecha:** 2026-07-17

## Resumen ejecutivo

Estructura del monorepo (`/backend /frontend /ai /contracts /docs /infra /scripts`), tooling de lint (ruff para Python, ESLint+TS para frontend), pre-commit, convenciones documentadas, plantillas de ADR/ADR-R/reporte de sprint.

## Archivos creados

`backend/pyproject.toml`, `frontend/package.json`, `.pre-commit-config.yaml`, `.gitattributes`, `.gitignore`, `docs/CONVENTIONS.md`, `docs/adr/TEMPLATE.md`, `docs/adr/ADR-R-TEMPLATE.md`, `docs/reports/SPRINT_TEMPLATE.md`, `docs/blocks/BLOCKS.md`, `README.md`.

## Archivos modificados

Ninguno (primer Sprint de código de esta WO).

## Bugs encontrados

Ninguno — Sprint de configuración, sin código ejecutable todavía.

## Bugs corregidos

N/A.

## Evidencias objetivas

- Estructura de directorios verificada con `ls` recursivo.
- `pyproject.toml` y `package.json` sintácticamente válidos (verificado en Sprints 3 y 5 al instalar dependencias reales sin error de parseo).

## Tiempo real (Wall Clock)

~10 minutos.

## Estado del Sprint

COMPLETO
