# ADÁN — Sistema Operativo Empresarial

ADÁN acompaña a una empresa desde el problema que quiere resolver hasta su operación. Lo hace con un **Board Room** de agentes ejecutivos (CEO, CFO, CTO, CMO…), una **memoria empresarial** (EMS) con búsqueda semántica, herramientas ejecutables (TEF), adquisición de conocimiento web (DKA) y un sistema operativo organizacional (OOS) de work orders, KPIs y riesgos.

**Estado:** Build C, línea oficial · versión 1.0.0 · estado **Piloto** (EPWO-029) · WO-090 a WO-093 cerradas.
**Stack:** FastAPI · React + TypeScript · PostgreSQL + pgvector · Ollama · Docker.

> Antes de abrir una Work Order nueva, lee el Canon: [`AD-ROOT-0001`](AD-ROOT-0001_Canon_del_Proyecto.md) y las [Reglas de Desarrollo](AD-GOV-0001_Reglas_de_Desarrollo.md) (Regla 1 y Fase -1 de la Regla 7). La próxima numeración libre es **WO-094**.

---

## Sincronizar la carpeta de la laptop

El repositorio oficial es `github.com/hernanjrestrepo/ADAN`, rama `laptop`. En la carpeta del proyecto:

```bash
git checkout laptop
git pull origin laptop
```

Al arrancar el backend por primera vez después del `pull`, la base SQLite existente (`backend/data/adan.db`) **se adopta y migra automáticamente, sin perder datos** (Alembic, `AD-DEC-0002 §D6`). Después, archiva el usuario de verificación de WO-090 (`AD-DEC-0002 §D2`):

```bash
cd backend
python -m scripts.archive_user wo090-verify@example.com
```

## Desarrollo

### Con Docker (recomendado)

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5174 · API: http://localhost:8050 (documentación en `/docs`)
- PostgreSQL + pgvector en `localhost:5433`, Ollama en `localhost:11434`. El modelo `DEFAULT_MODEL` se descarga al arrancar.

### Sin Docker

```bash
# Backend: Python 3.12; usa SQLite si no se define DATABASE_URL
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000

# Frontend: Node 22; el proxy de /api apunta a localhost:8000
cd frontend
npm ci
npm run dev        # http://localhost:5173
```

Para el chat y el Board Room hace falta Ollama. Fuera de Docker, define `OLLAMA_BASE_URL=http://localhost:11434` (el valor por defecto, `http://ollama:11434`, es el nombre del servicio en Docker).

## Pruebas y calidad

```bash
# Backend (SQLite en memoria; no necesita servicios externos)
cd backend
ruff check app tests migrations scripts
pytest

# Backend contra PostgreSQL + pgvector (con el PostgreSQL de `docker compose up`).
# Usa una base dedicada: su esquema se borra y se recrea en cada corrida.
docker compose exec postgres createdb -U adan adan_test   # solo la primera vez
TEST_DATABASE_URL=postgresql+psycopg://adan:CLAVE@localhost:5433/adan_test pytest

# Migraciones coherentes con los modelos
alembic check

# Frontend
cd frontend
npm run typecheck && npm test && npm run build
```

CI (`.github/workflows/ci.yml`) corre todo esto en cada push: lint, tests en ambos motores, cobertura ≥ 80%, auditoría de dependencias y build de las imágenes de producción.

## Producción

```bash
cp .env.example .env
# Obligatorio: JWT_SECRET (≥ 32 caracteres), POSTGRES_PASSWORD, CORS_ORIGINS
python -c "import secrets; print(secrets.token_urlsafe(48))"   # para JWT_SECRET
docker compose -f docker-compose.prod.yml up -d --build
```

- Solo se publica nginx (`HTTP_PORT`, por defecto 80). Pon TLS delante, en un balanceador o proxy.
- Con `ENVIRONMENT=production`, el backend **se niega a arrancar** con secretos de desarrollo, con SQLite o con CORS `*`, y desactiva `/docs`.
- Salud: `/health` (liveness) y `/health/ready` (base de datos y migraciones). Métricas Prometheus en `backend:8000/metrics`, solo en la red interna.
- Cada respuesta incluye `X-Request-ID`, que también aparece en los logs JSON del backend.

**Backups** (programarlos; ver deuda D-3 de WO-093):

```bash
docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U adan adan | gzip > adan-$(date +%F).sql.gz
```

### Migrar datos de SQLite a PostgreSQL

```bash
cd backend
python -m scripts.migrate_sqlite_to_postgres \
  --source sqlite:///data/adan.db \
  --target postgresql+psycopg://adan:CLAVE@localhost:5433/adan
```

El script se niega a escribir en un destino con datos, salvo con `--force`.

## Estructura

```
backend/
  app/
    api/v1/        auth, companies, nivel1 (Nivel 1 — El Dolor), cognitive
    agents/        Board Room ejecutivo y agente CEO
    ems/           Enterprise Memory System (ingesta, recuperación, vector store pgvector)
    tef/           Tool Execution Framework (herramientas para agentes)
    dka/           Adquisición de conocimiento web
    oos/           Organizational Operating System (work orders, KPIs, riesgos)
    integrations/  Gmail, Outlook, Calendar, Slack, REST (por usuario)
    core/          config, BD, migraciones, auth, acceso, seguridad, observabilidad
  migrations/      Alembic
  scripts/         migrate_sqlite_to_postgres, archive_user
  tests/           pytest (SQLite o PostgreSQL)
frontend/          React + TypeScript + Vite (Dockerfile.prod: nginx)
docs/              arquitectura, ADR, reportes de cierre de WO, evidencias
AD-*.md            gobierno: Canon, Historia, Reglas, Decisiones
```

## Seguridad: valores por defecto

| Variable | Default | Qué controla |
|---|---|---|
| `TEF_ENABLE_PYTHON_SANDBOX` | `false` | Ejecutar Python arbitrario desde agentes. Solo activar en un entorno aislado |
| `ALLOW_PRIVATE_HTTP` | `false` | Que TEF, DKA e integraciones llamen a la red interna (SSRF) |
| `TEF_FILES_DIR` | `backend/data/files` | Único directorio legible por `file_reader` |
| `AUTH_RATE_LIMIT_PER_MINUTE` | `20` | Intentos de login y registro por IP |

Todas las variables están en [`.env.example`](.env.example).

## Gobierno del proyecto

| Documento | Para qué |
|---|---|
| [`AD-ROOT-0001`](AD-ROOT-0001_Canon_del_Proyecto.md) | Canon: repositorio, rama, arquitectura y numeración de WO oficiales |
| [`AD-GOV-0001`](AD-GOV-0001_Reglas_de_Desarrollo.md) | Reglas de desarrollo (leer antes de cada WO) |
| [`AD-DEC-0001`](AD-DEC-0001_Historia_Oficial_de_ADAN.md) | Historia: cómo surgieron Build A, B y C |
| [`AD-DEC-0002`](AD-DEC-0002_Decisiones_de_Cierre_WO090-093.md) | Decisiones del cierre de WO-090 a WO-093 |
| [`CATALOGO_WORK_ORDERS.md`](CATALOGO_WORK_ORDERS.md) | Todas las WO y su estado |
| `REPORTE_CONSOLIDACION_WO090.md`, `docs/WO-09x_REPORTE_CIERRE.md` | Evidencia, deuda y riesgos de cada WO |
