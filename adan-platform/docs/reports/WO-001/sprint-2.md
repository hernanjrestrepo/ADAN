# WO-001 Sprint 2 — Infraestructura local + CI

**Célula:** A · **Fecha:** 2026-07-17

## Resumen ejecutivo

`docker-compose.yml` con PostgreSQL 16+pgvector, Redis, API y Web con healthchecks reales. Pipeline de CI (GitHub Actions): lint+unit, funcional contra Postgres/Redis reales como servicios, build de frontend, E2E nocturno vía Docker Compose. Ollama reutiliza el servicio del host (ADR-001) en vez de contenerizarse, evitando duplicar ~40GB de modelos ya descargados.

## Archivos creados

`infra/docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `.github/workflows/ci.yml`, `docs/adr/ADR-001-ollama-host-service.md`.

## Bugs encontrados

- Puertos por defecto (5432, 6379, 8000) ya estaban ocupados en la máquina de desarrollo por otros proyectos Paradixe corriendo en paralelo — se detectó *antes* de escribir el compose completo, verificando con `Test-NetConnection` puerto por puerto.

## Bugs corregidos

Se remapearon los puertos del host a 5436 (Postgres), 6382 (Redis), 8020 (API) — verificados libres los cuatro antes de fijarlos. 5173 (Web) ya estaba libre.

## Evidencias objetivas

- `docker compose config --quiet`: sintaxis válida.
- Verificación explícita de puertos libres/ocupados vía PowerShell `Test-NetConnection` antes de escribir la configuración final (no se descubrió el conflicto en producción, se previno).

## Tiempo real (Wall Clock)

~20 minutos.

## Estado del Sprint

COMPLETO
