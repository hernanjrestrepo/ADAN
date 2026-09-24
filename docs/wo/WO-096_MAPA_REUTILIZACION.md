# WO-096 — Mapa de reutilización de Build A (y de Build B) hacia Build C

**Fecha:** 2026-09-24 · **Ejecutor:** Claude Code
**Para qué sirve:** antes de escribir código nuevo en una WO, revisar aquí si ya existe algo que se pueda traer (EPWO-022). La Fase -1 de cada WO debe citar este mapa.
**Cómo se lee la columna "Decisión":**
- **Traer:** se copia casi igual.
- **Adaptar:** sirve como base, pero hay que ajustarlo a Build C.
- **Referencia:** solo como ejemplo; se escribe de nuevo.
- **Descartar:** no aplica.

Build A es archivo histórico (`AD-ROOT-0001 §6`). Nada se mueve de `adan-platform/`: se copia a Build C y la copia se cita en el commit.

---

## 1. Build A (`adan-platform/`) → Build C

| Pieza en Build A | Qué hace | Equivalente en Build C | Decisión | WO |
|---|---|---|---|---|
| `backend/migrations/versions/f8d91060004d_*.py` (619 líneas) | Esquema Alembic de 37 tablas: 26 de negocio y 11 operativas, sobre PostgreSQL | `backend/app/models/models.py` (SQLite, subconjunto) + bases EMS y OOS separadas | **Adaptar.** Es la base del esquema de AD-006 v1.2. Falta la entidad 38 y hay que reconciliarlo con las tablas propias de Build C (EMS, OOS, cognitivo) en una sola base declarativa. | WO-091 |
| `backend/app/models/*` (13 archivos) | Modelos SQLAlchemy de las 37 tablas, en español y con mixins de auditoría | `backend/app/models/models.py` | **Adaptar** junto con la migración. Los nombres de dominio en español siguen AD-003. | WO-091, WO-098 |
| `ai/memory/models.py`, `search.py`, `repository.py`, `hybrid_query.py`, `chunking.py`, `ingestion.py` | Grafo de conocimiento relacional (`kg_nodos`, `kg_aristas`) + memoria semántica con `pgvector` (768 dimensiones, `nomic-embed-text`, similitud coseno en Postgres) + consulta híbrida grafo y semántica | `backend/app/ems/*` (índice vectorial local de 128 dimensiones en memoria, `ems/store.py`) y `cognitive/knowledge_engine.py` | **Traer** la búsqueda `pgvector` y el modelo `MemoriaSemantica` para reemplazar `ems/store.py`. **Adaptar** la consulta híbrida al EMS. Hay que filtrar por empresa, no solo por proyecto. | WO-091 (vectores), WO-099 (memoria de 5 capas) |
| `backend/app/embeddings.py` | Embeddings reales vía Ollama `/api/embed` | `ems/providers.py` (`LocalEmbeddingProvider`, hash) | **Traer** como nuevo `EmbeddingProvider`. | WO-091 |
| `backend/app/routers/kg.py` (300 líneas) | API del grafo: nodos, aristas, recorrido e ingesta | No existe | **Adaptar.** Autentica, pero **no verifica que el proyecto sea del usuario** (`_user` no se usa): es el mismo tipo de fuga entre empresas que WO-094 cerró en Build C. Solo se trae con verificación de dueño. | WO-097, WO-099 |
| `ai/orchestrator/queue.py`, `executor.py`, `models.py` + `ai/worker.py` + `contracts/events/agent_execution.md` | Cola de ejecución de agentes sobre Redis, eventos de progreso y trabajador separado | Ejecución síncrona dentro de la petición (`agents/`, `cognitive/`) | **Adaptar** para los agentes por tiempo, que corren tareas largas fuera de la petición. Redis entra al stack. | WO-109 (agentes por tiempo), WO-093 |
| `ai/models/ollama_adapter.py` | Adaptador Ollama con reintentos, streaming, embeddings y salida estructurada | `backend/app/ai/ollama_adapter.py` (async, sin reintentos) | **Referencia.** Tomar los reintentos y la salida estructurada (JSON) para el enrutador de modelos; el de Build C ya es async. | WO-099 |
| `ai/agents/base.py`, `registry.py`, `tools.py`, `diagnostico.py` | Definición declarativa de agentes y registro | `agent_factory/`, `agents/base.py` | **Referencia** para el catálogo de agentes por tiempo. | WO-109 |
| `backend/app/auth/*` (JWT propio, ADR-002) | Login, dependencias y JWT | `backend/app/core/auth.py` | **Descartar.** Build C ya tiene el mismo esquema; lo que falta (secreto obligatorio, límite de intentos, revocación) no está en Build A. | — |
| `backend/app/errors.py` | Manejo global de errores con `DomainError` y respuestas estructuradas | Errores sueltos por router | **Traer.** | WO-097 |
| `backend/app/logging_config.py` | Logging estructurado | `backend/app/core/logging.py` (ya JSON) | **Descartar.** Build C ya lo tiene. | — |
| `infra/docker-compose.yml`, `Makefile` | Postgres 16 + pgvector + Redis, con puertos resueltos | `docker-compose.yml` (SQLite + Ollama) | **Adaptar:** agregar los servicios `postgres` y `redis`. | WO-091, WO-093 |
| `.github/workflows/ci.yml` (92 líneas) | CI con ruff, pruebas unitarias y pruebas funcionales con Postgres y Redis como servicios | No hay CI | **Adaptar** a la estructura de Build C (`backend/`, `frontend/`). | WO-093 |
| `.pre-commit-config.yaml` | Hooks de formato y lint | No hay | **Traer.** | WO-093 |
| `contracts/openapi/schema.json` | Contrato OpenAPI de la API de Build A | FastAPI genera `/openapi.json` | **Referencia.** El contrato se genera desde Build C y se prueba en CI. | WO-093 |
| `frontend/` (React + TypeScript + Playwright + ESLint) | Login, dashboard, agentes y explorador del grafo, con pruebas E2E | `frontend/` (React JSX, sin pruebas) | **Adaptar** la configuración (tsconfig, ESLint, Playwright) y el cliente de API tipado. Las pantallas de Build C se migran a TSX; el explorador del grafo se trae. | WO-092 |
| `ai/tests/*`, `backend/tests/*` (funcionales) | Pruebas contra Postgres y Ollama reales | `backend/tests/*` (SQLite) | **Adaptar** tras WO-091. | WO-091, WO-093 |
| `scripts/seed_demo.py` | Datos de demostración | — | **Descartar.** Contiene la contraseña de desarrollo `demo1234` (hallazgo S18). | — |
| `docs/blueprint/*` | Blueprint consolidado y AD-003 v1.2, AD-006 v1.2, AD-FUNC-07/08/09 | `docs/wo-000/` | **Traído en esta WO** (ver reporte WO-096). | WO-096 ✅ |
| `docs/adr/ADR-001`, `ADR-002` | Ollama como servicio del host; JWT propio | `docs/adr/ADR-001-Vertical-Nivel-1.md` | **Referencia.** Hay que renumerar si se traen, porque `ADR-001` choca con el de Build C (Regla 2). | — |

## 2. Build B (rama `adan/platform-integration`, tag `v1.0.0`) → Build C

Build B **todavía no está en este repositorio**. Su importación requiere la laptop (§3 del reporte WO-096). Según la auditoría y `CHAIN_CLOSURE.md`, cubre WO-000 → WO-012:
- Gemelo Digital v1
- Board Room con estrategias
- Scoring
- Experience y Gamification
- Onboarding
- Learning v1

Cuando se importe, esta sección se completa con el mismo formato. Candidatos a revisar primero:

| Pieza esperada en Build B | WO donde se usaría |
|---|---|
| Gemelo Digital v1 | WO-098 |
| Board Room con estrategias | WO-099, WO-117 |
| Scoring | WO-107 |
| Experience y Gamification | WO-116 |
| Onboarding | WO-108 |
| Learning v1 | WO-118 |

## 3. Regla de uso

1. La Fase -1 de cada WO cita las filas de este mapa que la afectan.
2. Lo que se trae se copia, no se mueve: `adan-platform/` queda intacto como historia.
3. Todo lo que se traiga pasa por las reglas de seguridad de WO-094 y WO-097: aislamiento por empresa, sin ejecución de código arbitrario y sin SSRF.
