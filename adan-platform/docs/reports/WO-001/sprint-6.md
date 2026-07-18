# WO-001 Sprint 6 — Baseline reproducible

**Célula:** A/B · **Fecha:** 2026-07-18

## Resumen ejecutivo

Stack completo (`postgres`, `redis`, `api`, `web`) levantado con `docker compose up -d --build` desde cero. Smoke E2E Playwright real (registro vía API → login vía UI → dashboard) contra el stack en Docker. Dos bugs reales encontrados y corregidos durante la verificación end-to-end. `Makefile` con targets `up/down/migrate/seed/test-backend/test-frontend-e2e/lint`. README actualizado con arranque real verificado.

## Archivos creados

`Makefile`, `frontend/e2e/smoke.spec.ts`, `docs/reports/WO-001/sprint-1.md`, `sprint-2.md`, `sprint-6.md`, `docs/reports/WO-001/closure.md`.

## Archivos modificados

`infra/docker-compose.yml` (bug real, ver abajo), `scripts/seed_demo.py` y `frontend/e2e/smoke.spec.ts` (bug real, ver abajo), `README.md`.

## Bugs encontrados

1. **Dominio de correo reservado.** `email-validator` (dependencia real de Pydantic `EmailStr`) rechaza `.local` como TLD de uso especial (RFC 6762/2606) — `demo@paradixe.local` y `@adan.local`, usados en `seed_demo.py` y el E2E, fallaban con `422 validation_error` al pasar por el endpoint real `/auth/register`. No se detectó leyendo el código — solo ejecutando contra la API real.
2. **Puerto incorrecto en variable de entorno del frontend.** `docker-compose.yml` fijaba `VITE_API_BASE_URL: http://localhost:8000`, pero el puerto real mapeado al host para `api` es `8020` (Sprint 2). El login desde el navegador real fallaba con "Not Found" porque el fetch iba al puerto equivocado — invisible en `docker compose config` (sintácticamente válido), solo visible ejecutando el E2E real contra el navegador.

## Bugs corregidos

1. Dominios reemplazados por `adan-demo.io` (no reservado) en `seed_demo.py` y `smoke.spec.ts`.
2. `VITE_API_BASE_URL` corregido a `http://localhost:8020`; contenedor `web` recreado; verificado con `docker exec adan-web-1 env`.

Ambos verificados con la suite E2E completa pasando después de cada corrección — no se declaró el bug "corregido" sin volver a ejecutar contra infraestructura real.

## Evidencias objetivas

- `docker compose up -d --build`: 4 contenedores (`postgres`, `redis`, `api`, `web`) — los 4 `healthy`/`running`.
- `curl http://localhost:8020/health/deep`: `{"status":"ok","checks":{"postgres":"ok","redis":"ok","ollama":"ok"}}` — **valida empíricamente ADR-001** (Ollama del host, alcanzado desde el contenedor `api` vía `host.docker.internal`).
- Playwright E2E contra el stack real en Docker: **2 passed** — registro real vía API, login real vía UI, dashboard visible con `/health` en vivo, y protección de ruta privada sin token.
- Migración de Alembic (37 tablas) y seed de datos demo, verificados contra el mismo Postgres containerizado.

## Tiempo real (Wall Clock)

~50 minutos (incluye 2 ciclos reales de debugging con evidencia, no solo lectura de código).

## Estado del Sprint

COMPLETO
