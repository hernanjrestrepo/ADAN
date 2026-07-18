# Cierre de WO-001 — Fundación Técnica

**Líder:** A · **Apoyo:** B, C, D · **Fecha de cierre:** 2026-07-18 · **Tag:** `wo-001-done`

## Resultado consolidado

Monorepo operativo. `docker compose up` levanta el sistema completo (Postgres 16+pgvector, Redis, API FastAPI, Web React) desde cero. CI configurado (lint+unit+funcional+build+E2E nocturno). Núcleo backend con auth JWT propia, manejo de errores, logging estructurado. 37 tablas del modelo de entidades (26 de negocio + 12 operativas de ADÁN, AD-005/AD-006) migradas y verificadas contra Postgres real. Shell de frontend con login real, ruta privada, dashboard con estado de salud en vivo. Smoke E2E completo verificado contra el stack real en Docker.

## Evidencias

- `docker ps`: 4 contenedores healthy/running desde `docker compose up -d --build`.
- `/health/deep`: Postgres + Redis + Ollama (del host) — los 3 `ok`, valida ADR-001 empíricamente.
- Alembic: 37 tablas aplicadas contra Postgres real (`\dt` verificado).
- `pytest`: 5 passed (2 funcionales contra Postgres real, corridos dos veces sin residuo).
- `ruff check .`: limpio. `npm run lint`: limpio. `npm run build`: exitoso.
- Playwright E2E: 2 passed contra el stack completo en Docker (no contra mocks).
- 2 bugs reales encontrados y corregidos durante la verificación end-to-end (dominio de correo reservado; puerto incorrecto en variable de entorno del frontend) — ninguno se habría detectado sin ejecutar contra infraestructura real.
- 10 commits en total para esta WO, un tag `wo-001-done` en el commit de cierre.

## Riesgos abiertos

- Auth JWT propia (ADR-002) es mínima — sin refresh tokens, sin rate limiting de login todavía (Fase de hardening, WO-011).
- El cliente API del frontend es tipado a mano, no generado desde OpenAPI — deuda técnica reconocida, se resuelve cuando el contrato de agentes (WO-002) estabilice.
- Ningún modelo de entidad tiene todavía datos reales de producción — solo el seed demo.

## Deuda técnica

- 2 vulnerabilidades de dependencias transitivas de ESLint 8.x (deprecado) — no bloqueante, ESLint 9 requiere migración de config (flat config), diferido.
- Cliente API del frontend manual, no generado — ver Riesgos.

## Dependencias externas

Ninguna nueva. Ollama del host (ya disponible, ADR-001) es la única dependencia externa real de esta WO, y ya estaba resuelta antes de empezar.

## Recomendación siguiente WO

Continuar con **WO-002 (Núcleo de Agentes y Orquestador)**, tal como fija la cadena. Ninguna desviación propuesta — la fundación técnica soporta directamente los requisitos de WO-002 (capa de abstracción de modelos sobre Ollama ya verificada como alcanzable desde el contenedor `api`).
