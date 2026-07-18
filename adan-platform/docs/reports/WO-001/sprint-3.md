# WO-001 Sprint 3 — Núcleo backend FastAPI

**Célula:** A · **Fecha:** 2026-07-17

## Resumen ejecutivo

App factory de FastAPI con configuración por entorno (pydantic-settings), logging estructurado JSON, manejo global de errores (DomainError/validación/HTTP/no capturados), autenticación JWT propia mínima (ADR-002, no reutilización de auth Paradixe por aislamiento deliberado del repo), endpoints `/health`, `/health/deep` (verifica Postgres/Redis/Ollama reales), `/metrics`.

## Archivos creados

`app/config.py`, `app/logging_config.py`, `app/db.py`, `app/errors.py`, `app/main.py`, `app/models/mixins.py` (Contrato Base), `app/models/usuario.py`, `app/auth/jwt.py`, `app/auth/dependencies.py`, `app/auth/router.py`, `app/routers/health.py`, `tests/conftest.py`, `tests/test_health.py`, `docs/adr/ADR-002-jwt-auth-propio.md`.

## Archivos modificados

`pyproject.toml` (package discovery, email-validator, marker `functional`, ignore B008 en ruff — falso positivo sobre el patrón idiomático de FastAPI).

## Bugs encontrados

- `setuptools` no descubría el paquete `app` sin declarar `[tool.setuptools.packages.find]` — falla al instalar en modo editable.
- Ruff (B008) marcaba como error el patrón idiomático `Depends()` en valores por defecto — es exactamente cómo FastAPI espera que se use.
- Import desordenado en `logging_config.py`.

## Bugs corregidos

Los tres anteriores, verificados con `ruff check .` limpio.

## Evidencias objetivas

- Entorno real Python 3.12.13 instalado vía `uv` (host trae 3.14 por defecto; el proyecto fija 3.12).
- `pip install -e ".[dev]"` exitoso — 40+ dependencias reales instaladas (FastAPI, SQLAlchemy 2, Alembic, psycopg, redis, python-jose, passlib, pytest).
- `ruff check .`: **All checks passed!**
- `pytest -v`: **3 passed** — `test_health_ok`, `test_metrics_ok`, `test_openapi_schema_available`, contra la app real (FastAPI `TestClient`, no mocks).
- `docker compose config` (Sprint 2) ya validado; Dockerfile del backend pendiente de build completo hasta Sprint 6 (baseline).

## Tiempo real (Wall Clock)

~35 minutos (incluye instalación de Python 3.12, resolución de dependencias, 2 rondas de fix de lint).

## Estado del Sprint

COMPLETO
