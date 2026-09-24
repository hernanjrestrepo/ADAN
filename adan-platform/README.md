# ADÁN — Sistema Operativo Empresarial

Agentes especializados, orquestación, gemelo digital, aprendizaje continuo y automatización empresarial. Primer usuario: Paradixe (dogfooding completo).

## Estado

En ejecución de la cadena WO-000 → WO-012 (`docs/blueprint/source/` para el Plan Maestro de Ejecución, `docs/reports/` para el progreso real de cada WO).

- **WO-000 (Blueprint Consolidado):** cerrada. Tag `blueprint-v1.0`.
- **WO-001 (Fundación Técnica):** en curso.

## Arranque rápido (verificado, WO-001 cerrada)

Requiere Docker Desktop y Ollama corriendo en el host (los modelos ya descargados en el host se reutilizan — ver ADR-001, no se conteneriza Ollama).

```bash
make up          # levanta postgres+pgvector, redis, api, web
make migrate     # aplica el esquema (37 tablas) contra Postgres real
make seed        # datos demo: una Empresa completa con Usuario/Proyecto/Nivel 1
```

- API: http://localhost:8020 (`/health`, `/health/deep` verifica Postgres+Redis+Ollama reales, `/docs`)
- Web: http://localhost:5173 (login → dashboard)

```bash
make test-backend       # pytest, incluye funcionales contra Postgres real
make test-frontend-e2e  # Playwright contra el stack completo en Docker
make lint                # ruff (backend) + eslint (frontend)
```

**Puertos no-default:** se eligieron 5436/6382/8020 tras detectar que 5432/6379/8000 ya estaban ocupados por otros servicios en la máquina de desarrollo — ver `docs/reports/WO-001/sprint-2.md`.

## Estructura

```
/backend    Python 3.12, FastAPI, SQLAlchemy 2, Alembic
/frontend   React 18, Vite, Tailwind
/ai         Runtime de agentes propio (sin frameworks de terceros)
/contracts  OpenAPI + esquemas de eventos — frontera entre células
/docs       Blueprint, ADRs, reportes, bloqueos
/infra      Docker Compose, scripts de infraestructura
/scripts    Utilidades de desarrollo
```

Ver `docs/CONVENTIONS.md` para las convenciones completas del monorepo.
