# ADÁN — Sistema Operativo Empresarial

Agentes especializados, orquestación, gemelo digital, aprendizaje continuo y automatización empresarial. Primer usuario: Paradixe (dogfooding completo).

## Estado

En ejecución de la cadena WO-000 → WO-012 (`docs/blueprint/source/` para el Plan Maestro de Ejecución, `docs/reports/` para el progreso real de cada WO).

- **WO-000 (Blueprint Consolidado):** cerrada. Tag `blueprint-v1.0`.
- **WO-001 (Fundación Técnica):** en curso.

## Arranque rápido (una vez completado WO-001)

```bash
docker compose -f infra/docker-compose.yml up
```

Levanta PostgreSQL 16 + pgvector, Redis, Ollama, la API y el frontend.

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
