# Inventario Técnico — ADÁN Build C (WO-090, Sprint 3)

**Fecha:** 2026-07-31 · **Alcance:** `repos-active/adan/{backend,frontend,docs,docker-compose.yml}` (Build C, ahora línea oficial). Generado por análisis estático (grep/AST de nombres) y una consulta directa a la base de datos real — no por ejecución del sistema (eso es Sprint 4).

---

## 1. APIs / Endpoints — 65 en total, 12 routers

| Router | Prefijo/archivo | Endpoints |
|---|---|---|
| `v1` (agrega auth+companies+nivel1+cognitive) | `api/v1/router.py` | 4 sub-routers |
| ⤷ auth | `api/v1/auth.py` | `POST /register`, `POST /login`, `GET /me` |
| ⤷ companies | `api/v1/companies.py` | `POST /`, `GET /`, `GET /{id}`, `GET /{id}/project` |
| ⤷ nivel1 | `api/v1/nivel1.py` | 9 endpoints: status, chat, chat-stream, board-room, diagnosis, recommendations, gate-review, scores, documents |
| ⤷ cognitive | `api/v1/cognitive.py` | `POST /think`, `GET /health` |
| agents | `agents/api.py` | `POST /ceo`, `GET /health` |
| board | `agents/board_api.py` | `POST /run`, `GET /health` |
| dka | `dka/api.py` | `POST /acquire`, `GET /health` |
| ems | `ems/api.py` | `POST /ingest`, `POST /retrieve`, `GET /documents/{id}`, `GET /stats/{id}`, `POST /correct`, `GET /health` |
| integrations | `integrations/api.py` | 5 endpoints (connectors, connect, disconnect, execute, health) |
| voice | `voice/api.py` | `POST /stt`, `POST /tts`, `GET /health` |
| omnichannel | `omnichannel/api.py` | 4 endpoints (channels, receive, respond, health) |
| oos | `oos/api.py` | 13 endpoints (work orders, dashboard, KPIs, risks, review, meetings, health) |
| tef | `tef/api.py` | `GET /tools`, `POST /discover`, `POST /execute`, `GET /audit/{id}`, `GET /health` |

**Verificado, no asumido:** los 10 routers de nivel superior están importados y montados en `backend/app/main.py`; el router `cognitive` no aparece ahí directamente porque está anidado dentro de `v1_router` (`api/v1/router.py`) — se verificó el archivo para confirmar que sí está montado, no se asumió.

## 2. Modelos de datos — 39 clases ORM, 30 tablas reales confirmadas en la base de datos

- `backend/app/models/models.py`: 18 clases (`User`, `Company`, `FoundingNarrative`, `Project`, `Level`, `Card`, `Conversation`, `Message`, `Score`, `Decision`, `Document`, `Event`, más 6 enums).
- `backend/app/ems/models.py`: 5 clases (`EMSDocument`, `EMSChunk`, `EMSVersion`, `KnowledgeFact`, `Correction`) — **base declarativa propia (`EMSBase`), separada de la base principal.**
- `backend/app/oos/models.py`: 16 clases (`Organization`, `BusinessUnit`, `Department`, `Role`, `Objective`, `KPI`, `Initiative`, `DecisionRecord`, `WorkOrder`, `Task`, `Assignment`, `ProgressReport`, `Risk`, `Meeting`, `MeetingMinute`) — **también con base declarativa propia (`OOSBase`).**
- **Tablas reales confirmadas** (consulta directa a `backend/data/adan.db`, base con datos, no vacía): 30 tablas — `users, companies, founding_narratives, projects, levels, scores, decisions, documents, events, cards, conversations, messages, ems_documents, ems_facts, ems_chunks, ems_versions, ems_corrections, oos_organizations, oos_business_units, oos_objectives, oos_decisions, oos_risks, oos_meetings, oos_departments, oos_kpis, oos_initiatives, oos_work_orders, oos_meeting_minutes, oos_roles, oos_tasks, oos_assignments, oos_progress_reports`.
- **Nota estructural sin resolver por este inventario:** el módulo principal, `ems` y `oos` usan **tres bases declarativas SQLAlchemy separadas** (`Base`, `EMSBase`, `OOSBase`) en vez de una sola. Funciona porque SQLite las escribe todas en el mismo archivo, pero es una fragmentación real de esquema, no solo de código — relevante para la migración a Postgres (WO-091).

## 3. Agentes — dos mecanismos distintos coexisten

1. **Basado en clases:** `ExecutiveAgent` (clase abstracta, `agents/base.py`) → `CEOAgent` (`agents/ceo.py`) y `ConfigurableAgent` (`agent_factory/factory.py`, permite definir agentes por configuración).
2. **Basado en diccionario de prompts:** `agents/board.py` define `BOARD_AGENTS` con **7 roles** (CEO, CFO, COO, CMO, CTO, CLO, CHRO) y `DEBATE_ORDER` — coincide con los "7 roles" de `AD-FUNC-02_Board_Room_v1.0.md`. Este es un mecanismo independiente del basado en clases, no una extensión de él.

## 4. Herramientas (TEF — Tool Execution Framework)

`backend/app/tef/tools.py`: 6 `ToolProvider` — `CalculatorTool`, `FileReaderTool`, `HttpRequestTool`, `SqlQueryTool`, `PythonSandboxTool`, `EmailSenderTool` — más `ToolRegistry` (`tef/registry.py`) para descubrimiento/ejecución vía `POST /tef/execute`.

**Nota de riesgo, no evaluada en profundidad en este Sprint:** `PythonSandboxTool` y `SqlQueryTool` son herramientas de ejecución de código/consultas arbitrarias expuestas a agentes — su superficie de seguridad no se auditó en este inventario (es un inventario, no una revisión de seguridad).

## 5. Eventos

`backend/app/cognitive/event_bus.py`: `CognitiveEvent` (estructura de evento) + `EventBus` (despachador). No se encontró un catálogo cerrado de tipos de evento (`EventType` enum) — el bus parece aceptar eventos con tipo libre, a diferencia del `Event` con tipo controlado de Build B.

## 6. Tests

19 archivos en `backend/tests/`, **214 funciones `test_` en total** (conteo por grep, no por ejecución — ver Sprint 4 para resultados de ejecución real).

## 7. Dependencias declaradas

**Backend** (`backend/requirements.txt`): `fastapi==0.115.0`, `uvicorn[standard]==0.30.6`, `sqlalchemy==2.0.35`, `pydantic[email]==2.9.2`, `python-jose[cryptography]==3.3.0`, `passlib[bcrypt]==1.7.4`, `bcrypt==4.2.1`, `httpx==0.27.2`, `python-multipart==0.0.12`.

**Ausente del archivo de dependencias (hallazgo, no crítica):** `pytest` no está declarado en `requirements.txt` a pesar de que existen 214 funciones de test — instalar solo `requirements.txt` no permite correr la suite. Tampoco hay `alembic` (consistente con no usar migraciones sobre SQLite) ni `psycopg2`/`asyncpg` (consistente con no usar Postgres todavía — será necesario agregarlo en WO-091).

**Frontend** (`frontend/package.json`): `react@18.3.1`, `react-dom@18.3.1`, `react-router-dom@6.26.2`, `react-markdown@9.0.1`; dev: `vite@5.4.3`, `tailwindcss@3.4.10`, `@vitejs/plugin-react`. **Confirmado (no solo por extensión de archivo): no hay `typescript` ni `@types/*` de producción en `devDependencies`** — el frontend es JavaScript puro, consistente con los archivos `.jsx` ya identificados en la auditoría genealógica.

## 8. Docker

`docker-compose.yml` (raíz): 4 servicios — `backend` (8050→8000), `frontend` (5174→5173), `ollama` (imagen `ollama/ollama:latest`, 11434), `model-pull` (imagen `curlimages/curl`, probablemente para descargar el modelo al iniciar). Volúmenes nombrados: `backend-data`, `ollama-models`.

## 9. Variables de entorno

`.env.example` (raíz): solo dos variables — `JWT_SECRET` (con advertencia explícita "CHANGE IN PRODUCTION!") y `DEFAULT_MODEL=qwen2.5:0.5b`. No hay `DATABASE_URL` expuesta — la ruta de SQLite probablemente está hardcodeada en `app/core/config.py` (no verificado línea por línea en este Sprint).

---

## Brechas de este inventario (honestas)

- No se abrió cada archivo línea por línea — el inventario es de superficie (nombres, firmas, conteos), no una revisión de código completa.
- No se evaluó la calidad ni corrección del código, solo su existencia y estructura.
- La superficie de seguridad de `PythonSandboxTool`/`SqlQueryTool` queda señalada, no evaluada.
