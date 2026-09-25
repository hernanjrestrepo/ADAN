# ADAN

Sistema operativo empresarial de Paradixe: agentes especializados (Board de 7 roles), memoria empresarial (EMS), ejecución de herramientas (TEF), gestión operativa (OOS), adquisición de conocimiento (DKA), voz y omnicanal, sobre modelos locales vía Ollama.

Este repositorio reúne en un solo lugar todo el código de ADAN que existía por separado.

## Qué hay en este repositorio

| Ubicación | Qué es | Estado | Origen |
|---|---|---|---|
| Raíz: `backend/`, `frontend/`, `docs/`, `scripts/`, `docker-compose.yml` | **Build C**, "Vertical Nivel 1". FastAPI + PostgreSQL/pgvector (SQLite en desarrollo y pruebas) + React 19 con TypeScript + Ollama. | **Línea oficial** (`AD-DEC-0001 §5.1`) | Carpeta `repos-active/adan` de la laptop. No tenía historial de git; su primer commit es `abc6b6c`. |
| `adan-platform/` | **Build A**. Monorepo FastAPI + PostgreSQL/pgvector + React/TypeScript, WO-000 → WO-003. | Archivo histórico, sin más desarrollo (`AD-DEC-0001 §5.2`) | Repo local sin remote. Sus 25 commits se conservan. |
| `autonomous/` | Prototipo de 2024: Lambda que crea clones de sí misma, código autogenerado y despliegue con CodePipeline/CodeBuild. | Histórico | `hernanjrestrepo/adan_autonomous`. Sus 14 commits se conservan (último original: `2fab0bc`). |

**Build B** (rama `adan/platform-integration` del monorepo compartido `Paradixe/repos`, WO-000 → WO-012, tag `v1.0.0`) no está aquí: sigue viviendo en ese monorepo como referencia técnica (`AD-DEC-0001 §5.3`).

`hernanjrestrepo/ADAN-BACK` estaba vacío (sin commits), así que no aportó contenido.

Los historiales importados se reescribieron para vivir bajo su carpeta, con autores y fechas intactos: `git log -- adan-platform/` y `git log -- autonomous/`.

## Estado actual (2026-09-25)

**Avance: ~40 %** hacia ADÁN Enterprise v1 (era ~22 % en la auditoría). Están cerrados H1 (base segura), H2 (plataforma enterprise: PostgreSQL, seguridad por empresa, frontend TypeScript, CI y producción) y WO-099 (IA por complejidad con Claude, Board Room de 7 roles y memoria en cinco capas). Lo siguiente en H3: WO-098 Gemelo Digital, WO-107, WO-108 y WO-109.

Qué se hizo, qué falta, cuándo se puede ver la plataforma y qué le toca a Hernán: **`docs/ESTADO_ADAN_2026-09-25.md`**.

## Por dónde empezar

0. `docs/ESTADO_ADAN_2026-09-25.md`: resumen del estado y de lo pendiente.
1. `AD-ROOT-0001_Canon_del_Proyecto.md`: repositorio, rama, arquitectura y numeración oficiales. Leer antes de escribir código.
2. `AD-DEC-0001_Historia_Oficial_de_ADAN.md`: por qué existen tres builds y cuál es la oficial.
   `AD-DEC-0002_Modelo_de_Negocio_y_Ecosistema.md`: qué hace ADÁN dentro de Paradixe, cómo se monetiza y qué decidió Hernán el 2026-09-24.
3. `AD-GOV-0001_Reglas_de_Desarrollo.md`: reglas de proceso.
4. `REPORTE_CONSOLIDACION_WO090.md`: estado de Build C al 2026-07-31 (WO-090 abierta).
5. `docs/wo-000/BLUEPRINT_ADAN_v1.1.md`: mapa del blueprint (qué versión de cada documento está vigente y qué está implementado).
   `docs/wo-000/00-fundamentos/AD-000_Paradixe_Ecosystem_Vision_v2.0.md`: el ecosistema Paradixe según AD-DEC-0002.
6. `docs/auditoria/AUDITORIA_ADAN_2026-09.md`: auditoría completa del código, avance de partida (~22 %), bugs y brechas frente al blueprint.
7. `docs/auditoria/PLAN_WO_ADAN_100.md`: plan de Work Orders propuesto para llegar al 100 %.
8. `docs/wo/`: reportes de cierre de cada Work Order, con su evidencia, y el mapa de reutilización de Build A (`WO-096_MAPA_REUTILIZACION.md`).
9. `docs/operacion/RUNBOOK.md`: cómo desplegar, revertir, respaldar y observar ADÁN en producción.

Este repositorio y su rama `main` son los oficiales desde el 2026-09-24 (`AD-ROOT-0001 §1-2`).

## Arranque rápido (Build C)

```bash
export JWT_SECRET=<un-secreto-propio>   # obligatorio fuera de desarrollo
docker compose up --build
```

- API: http://localhost:8050 (`/health`, `/docs`)
- Web: http://localhost:5174
- PostgreSQL 16 + pgvector: `localhost:5432`, base `adan`. La contraseña sale de `POSTGRES_PASSWORD`.
- Ollama: http://localhost:11434. El modelo por defecto es `qwen2.5:0.5b` (`DEFAULT_MODEL`). Los embeddings del EMS usan `nomic-embed-text`. El servicio `model-pull` descarga los dos.

### Seguridad (WO-097)

| Variable | Para qué |
|---|---|
| `ADAN_ENV` | `development` (por defecto), `test` o `production`. En `production` la app no arranca si falta `JWT_SECRET` (mínimo 32 caracteres) o `ENCRYPTION_KEY`, si la base es SQLite o si la clave de PostgreSQL es la de desarrollo. |
| `JWT_SECRET` | Firma de las sesiones. Si no se define, en desarrollo se genera una al azar en cada arranque y las sesiones se pierden al reiniciar. |
| `ENCRYPTION_KEY` | Cifra las credenciales de los conectores. Se genera con `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. |
| `RATE_LIMIT_PER_MINUTE`, `LLM_RATE_LIMIT_PER_MINUTE`, `LOGIN_MAX_FAILURES`, `REGISTER_PER_IP_PER_HOUR`, `MAX_BODY_BYTES` | Límites por IP, por usuario (endpoints que usan el LLM), de intentos de login, de registros y de tamaño de las solicitudes. |
| `REDIS_URL` | Límites compartidos entre workers y réplicas. Sin Redis, los límites viven en la memoria de cada proceso. |
| `SANDBOX_URL`, `SANDBOX_TOKEN` | Sandbox aislado (`sandbox/`) para ejecutar Python. Sin ellos, `python_sandbox` no existe. |
| `METRICS_TOKEN` | Protege `/metrics` (Prometheus). |
| `ANTHROPIC_API_KEY`, `LLM_MODEL_STANDARD`, `LLM_MODEL_COMPLEX`, `LLM_MODEL_FAST` | IA por complejidad (WO-099). Ollama hace lo simple; Claude Sonnet, la conversación y el diagnóstico; Claude Opus, los votos del Board. Sin clave, todo corre en Ollama marcado como degradado. `python scripts/check_claude.py` verifica la clave. El costo por empresa y Nivel está en `GET /api/v1/companies/{id}/llm-usage`. |
| `OUTBOUND_ALLOWED_HOSTS` | Hosts a los que pueden llamar las herramientas y conectores. Vacío = cualquier host público. El proxy de salida se configura con `HTTPS_PROXY`. |

La interfaz web guarda la sesión en una cookie httpOnly. Las peticiones que modifican datos llevan la cabecera `X-Requested-With: adan`, que funciona como protección anti-CSRF. Los clientes de la API pueden seguir usando `Authorization: Bearer`.

El backend aplica las migraciones de Alembic al arrancar (`backend/migrations`). Para crear una migración nueva:

```bash
cd backend
alembic revision --autogenerate -m "qué cambia"
```

Para pasar los datos de una base SQLite anterior a PostgreSQL:

```bash
cd backend
python -m app.core.sqlite_to_postgres --from sqlite:///data/adan.db --to postgresql://adan:<clave>@localhost:5432/adan
```

Pruebas del backend:

```bash
cd backend
pip install -r requirements-dev.txt
pytest                                                                     # SQLite en memoria
TEST_DATABASE_URL=postgresql://adan:<clave>@localhost:5432/adan_test pytest  # PostgreSQL + pgvector
```

`tests/test_stress.py` necesita el backend levantado en `localhost:8050`, con Ollama y con `REGISTER_PER_IP_PER_HOUR` alto, porque simula muchos usuarios desde una sola IP.

Frontend (Node 22 o más reciente):

```bash
cd frontend
npm ci
npm run dev          # http://localhost:5173
npm run typecheck    # TypeScript
npm run lint         # ESLint
npm run build
npm run test:e2e     # Playwright con el API simulado; no necesita backend
```

Si ya hay un Chromium instalado, `PW_CHROMIUM_PATH=/ruta/a/chromium npm run test:e2e` lo usa. Si no, primero `npx playwright install chromium`.

Sin Docker, `.claude/launch.json` levanta el backend en `:8020` y el frontend en `:5173`. El proxy de Vite apunta a `:8020`; para otro backend, define `ADAN_API_URL`.

## Producción (WO-093)

- `docker-compose.prod.yml`:
  - nginx es lo único publicado;
  - PostgreSQL, Redis y el sandbox van en redes internas;
  - las migraciones corren en un paso aparte.
- `scripts/deploy.sh`, `rollback.sh`, `backup.sh` y `restore.sh`. Guía completa: [`docs/operacion/RUNBOOK.md`](docs/operacion/RUNBOOK.md).
- CI en GitHub Actions (`.github/workflows/ci.yml`), con tres jobs:
  - **backend**: SQLite, PostgreSQL y Redis, migraciones, `pip-audit` y backup/restauración;
  - **frontend**: tipos, lint, build, `npm audit` y E2E;
  - **stack de producción** con Docker: despliegue, prueba de humo con el aislamiento del sandbox, backup, rollback y restauración.

## Despliegue de `autonomous/`

Si se conecta un proyecto de CodeBuild a este repositorio, configura la ruta del buildspec como `autonomous/buildspec.yml`. CodeBuild ejecuta los comandos desde la raíz del repo, por eso las pruebas se invocan con `pytest autonomous/tests/`.
