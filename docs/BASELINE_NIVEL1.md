# ADÁN — Baseline Oficial Nivel 1

**Versión:** 1.0  
**Fecha de Congelación:** 2026-07-24  
**WO de Origen:** WO-001 (Cerrada)  
**Estado:** CONGELADO — No modificable sin Work Order específica

---

## 1. Arquitectura Final

### 1.1 Stack Tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Backend | Python 3.12 + FastAPI | 0.115.0 |
| Frontend | React 18 + Vite + Tailwind | 5.4.3 |
| Base de Datos | SQLite (WAL mode) | — |
| IA | Ollama + Qwen 2.5 | 0.5b (Q4_K_M) |
| Autenticación | JWT + bcrypt | python-jose 3.3.0 |
| ORM | SQLAlchemy | 2.0.35 |
| Infraestructura | Docker Compose | 4 servicios |

### 1.2 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                     DOCKER COMPOSE                       │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│  │   Frontend   │───▶│   Backend    │───▶│  Ollama   │  │
│  │  React/Vite  │    │   FastAPI    │    │ Qwen 2.5  │  │
│  │   :5174      │    │   :8050      │    │  :11434   │  │
│  └──────────────┘    └──────┬───────┘    └───────────┘  │
│                             │                            │
│                   ┌─────────▼─────────┐                  │
│                   │    SQLite DB      │                  │
│                   │   /app/data/      │                  │
│                   │   adan.db         │                  │
│                   └───────────────────┘                  │
│                                                          │
│  ┌──────────────┐                                        │
│  │  model-pull  │  (init container, pulls Qwen model)   │
│  └──────────────┘                                        │
└─────────────────────────────────────────────────────────┘
```

### 1.3 Arquitectura Backend por Capas

```
app/
├── core/           # Fundación: config, database, auth, logging
├── models/         # SQLAlchemy ORM (11 tablas)
├── schemas/        # Pydantic request/response (15 schemas)
├── api/v1/         # Endpoints REST (3 routers: auth, companies, nivel1)
├── ai/             # Capa de IA desacoplada (patrón adapter)
├── nivel1/         # Lógica de negocio: Board Room, Gate Review, Service
└── services/       # Compartidos: Gemelo Digital, Memory
```

### 1.4 Principios Arquitectónicos

- **Contrato Base (AD-006):** Todas las entidades heredan: UUID id, version, status, created_at, updated_at, created_by, confidence_level
- **Append-only Events:** Nada se elimina, solo se archiva (status=archived)
- **Adapter Pattern:** Capa de IA desacoplada del proveedor
- **Determinismo en Gate Review:** 0 llamadas a LLM para evaluación

---

## 2. Flujo Completo del Nivel 1

```
1. Registro         POST /api/v1/auth/register       → JWT
2. Login            POST /api/v1/auth/login           → JWT
3. Crear Empresa    POST /api/v1/companies/           → Company + Project + 7 Levels
4. Chat             POST /api/v1/nivel1/{id}/chat     → Respuesta LLM
5. Board Room       POST /api/v1/nivel1/{id}/board-room  → 4 agentes concurrentes
6. Diagnóstico      POST /api/v1/nivel1/{id}/diagnosis    → Documento
7. Recomendaciones  POST /api/v1/nivel1/{id}/recommendations → Documento
8. Gate Review      POST /api/v1/nivel1/{id}/gate-review   → Score 80/100
9. Nivel Completo   → Siguiente nivel activado
```

---

## 3. APIs — Endpoints Congelados

Base URL: `/api/v1`

### 3.1 Auth (`/api/v1/auth`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/auth/register` | No | Registrar usuario (email, name, password) → JWT + user |
| POST | `/auth/login` | No | Login (email, password) → JWT + user |
| GET | `/auth/me` | Sí | Obtener perfil del usuario actual |

### 3.2 Companies (`/api/v1/companies`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/companies/` | Sí | Crear empresa (auto-crea Project + 7 Levels + FoundingNarrative) |
| GET | `/companies/` | Sí | Listar empresas del usuario |
| GET | `/companies/{id}` | Sí | Obtener empresa específica |
| GET | `/companies/{id}/project` | Sí | Obtener proyecto de la empresa |

### 3.3 Nivel 1 (`/api/v1/nivel1`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/nivel1/{id}/status` | Sí | Estado completo del Nivel 1 |
| POST | `/nivel1/{id}/chat` | Sí | Enviar mensaje de chat → respuesta IA |
| POST | `/nivel1/{id}/chat-stream` | Sí | Chat con streaming via SSE |
| POST | `/nivel1/{id}/board-room` | Sí | Ejecutar Board Room (4 agentes) |
| POST | `/nivel1/{id}/diagnosis` | Sí | Generar documento de diagnóstico |
| POST | `/nivel1/{id}/recommendations` | Sí | Generar recomendaciones |
| POST | `/nivel1/{id}/gate-review` | Sí | Ejecutar Gate Review determinístico |
| GET | `/nivel1/{id}/scores` | Sí | Obtener todos los scores |
| GET | `/nivel1/{id}/documents` | Sí | Obtener todos los documentos |

### 3.4 Root

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/` | Info de la app (nombre, versión, link a docs) |

---

## 4. Modelos de Datos

### 4.1 Modelos SQLAlchemy (11 tablas)

Todas las entidades heredan el **Contrato Base** (AD-006).

| Modelo | Tabla | Campos Clave | Relaciones |
|---|---|---|---|
| `User` | `users` | email, name, hashed_password, role (user/primary_user) | companies |
| `Company` | `companies` | name, description, industry, country, maturity (0-1) | primary_user, projects, founding_narrative |
| `FoundingNarrative` | `founding_narratives` | origin_story, founding_motivation, irreversible_commitment | company (1:1) |
| `Project` | `projects` | name, company_id | company, levels, cards, scores, decisions, documents, events |
| `Level` | `levels` | number (1-7), name, status (blocked/active/completed), completed_at | project, cards |
| `Card` | `cards` | title, description, card_type, status (blocked/active/completed) | project, level, conversations |
| `Conversation` | `conversations` | title, summary | card, messages |
| `Message` | `messages` | role, agent_name, content, metadata_json | conversation |
| `Score` | `scores` | score_type (problem/solution/business/product/market/execution), value (0-100), confidence_level, reasoning, evidence (JSON) | project |
| `Decision` | `decisions` | title, description, proposed_by, approved_by, status (proposed/approved/rejected/executed), reasoning, disagreement, confidence_level | project |
| `Document` | `documents` | title, content, doc_type, origin (generated_by_adan/received_from_client) | project |
| `Event` | `events` | event_type, entity_type, entity_id, data (JSON) | project |

### 4.2 Enums

| Enum | Valores |
|---|---|
| `EntityStatus` | active, archived |
| `UserRole` | user, primary_user |
| `NivelStatus` | blocked, active, completed |
| `CardStatus` | blocked, active, completed |
| `DecisionStatus` | proposed, approved, rejected, executed |
| `ScoreType` | problem, solution, business, product, market, execution |

### 4.3 Schemas Pydantic (15 schemas)

| Schema | Tipo | Propósito |
|---|---|---|
| `UserRegister` | Request | email, name, password |
| `UserLogin` | Request | email, password |
| `TokenResponse` | Response | access_token, token_type, user |
| `UserResponse` | Response | id, email, name, role |
| `CompanyCreate` | Request | name, description, industry, country |
| `CompanyResponse` | Response | id, name, description, industry, country, maturity, status, version, created_at |
| `ProjectResponse` | Response | id, company_id, name, status, version, created_at |
| `LevelResponse` | Response | id, project_id, number, name, status, completed_at |
| `CardResponse` | Response | id, level_id, title, description, card_type, status |
| `ConversationResponse` | Response | id, card_id, title, status, summary, created_at |
| `MessageCreate` | Request | content |
| `MessageResponse` | Response | id, conversation_id, role, agent_name, content, created_at |
| `ScoreResponse` | Response | id, project_id, score_type, value, confidence_level, reasoning, created_at |
| `DecisionResponse` | Response | id, project_id, title, description, proposed_by, status, reasoning, confidence_level, created_at |
| `ChatRequest` | Request | message, conversation_id (optional) |
| `ChatResponse` | Response | message (MessageResponse), conversation_id, card_id |
| `DashboardResponse` | Response | company, project, current_level, scores, recent_decisions, progress |
| `GateReviewRequest` | Request | level_number |
| `GateReviewResponse` | Response | approved, scores, decisions, level_status, message |

---

## 5. Base de Datos

- **Motor:** SQLite con WAL mode y foreign keys habilitadas
- **Archivo:** `backend/data/adan.db`
- **Tablas:** 11 (users, companies, founding_narratives, projects, levels, cards, conversations, messages, scores, decisions, documents, events)
- **Creación de schema:** `Base.metadata.create_all()` al inicio (sin Alembic aún)
- **Relaciones:** Users → Companies → Projects → Levels/Cards/Conversations/Messages/Scores/Decisions/Documents/Events
- **Principio de diseño:** Tabla Events append-only; nada se elimina, solo se archiva

---

## 6. Docker

### 6.1 Servicios (4)

| Servicio | Imagen/Build | Puerto | Propósito |
|---|---|---|---|
| `backend` | Build `./backend` (Python 3.12-slim) | 8050:8000 | Backend FastAPI |
| `frontend` | Build `./frontend` (Node 20-slim) | 5174:5173 | Servidor dev React/Vite |
| `ollama` | `ollama/ollama:latest` | 11434:11434 | Inferencia LLM local |
| `model-pull` | `curlimages/curl:latest` | — | Init container, descarga modelo Qwen |

### 6.2 Volúmenes

- `backend-data`: Datos SQLite (`/app/data`)
- `ollama-models`: Pesos del modelo (`/root/.ollama`)

### 6.3 Healthcheck

- Ollama: TCP healthcheck en puerto 11434
- Backend depende de: Ollama healthy + model-pull completado

### 6.4 Backend Dockerfile

```dockerfile
FROM python:3.12-slim
# Instala curl, dependencias pip, copia app, ejecuta start.sh
# start.sh espera Ollama, luego ejecuta uvicorn con --reload
```

### 6.5 Frontend Dockerfile

```dockerfile
FROM node:20-slim
# npm install, copia fuente, ejecuta npm run dev --host 0.0.0.0
```

---

## 7. Variables de Entorno

### 7.1 Root `.env`

| Variable | Default | Propósito |
|---|---|---|
| `JWT_SECRET` | `adan-dev-secret-change-in-production` | Secret para firmar JWT |
| `DEFAULT_MODEL` | `qwen2.5:0.5b` | Modelo Ollama a descargar/usar |

### 7.2 Backend `.env`

| Variable | Default | Propósito |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/adan.db` | String de conexión a BD |
| `JWT_SECRET` | `adan-dev-secret-change-in-production` | Secret para firmar JWT |
| `JWT_EXPIRATION_MINUTES` | `1440` (24h) | Expiración del token |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Endpoint de Ollama |
| `DEFAULT_MODEL` | `qwen2.5:0.5b` | Modelo LLM por defecto |
| `AI_TIMEOUT_SECONDS` | `120` | Timeout de llamadas LLM |
| `LLM_PROVIDER` | `ollama` | Proveedor de IA (clave del registry) |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Orígenes permitidos CORS |

---

## 8. Dependencias

### 8.1 Backend (`requirements.txt`)

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
pydantic[email]==2.9.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.2.1
httpx==0.27.2
python-multipart==0.0.12
```

### 8.2 Frontend (`package.json`)

**Dependencias:**
- react ^18.3.1
- react-dom ^18.3.1
- react-router-dom ^6.26.2
- react-markdown ^9.0.1

**Dev Dependencies:**
- vite ^5.4.3
- @vitejs/plugin-react ^4.3.1
- tailwindcss ^3.4.10
- postcss ^8.4.45
- autoprefixer ^10.4.20

---

## 9. Modelos IA Utilizados

### 9.1 Modelo Activo

- **Qwen 2.5:0.5b** (379.4 MB, 494M params, Q4_K_M quantization, 32K context)
- **Ejecución:** CPU only (sin GPU detectada en Docker)
- **Descarga automática** por init container `model-pull` en primer arranque

### 9.2 Arquitectura de Capa IA

```
LLMAdapter (ABC)
  ├── OllamaAdapter (actual, local Qwen 2.5:0.5b)
  ├── OpenAIAdapter (planeado)
  └── AnthropicAdapter (planeado)
```

- **Factory basado en registry:** `get_llm_adapter()` lee `LLM_PROVIDER`, lazy-import el adaptador correcto
- **Actualmente solo `ollama`** registrado; OpenAI/Anthropic stubbed como entradas futuras

### 9.3 Puntos de Uso de IA

| Punto | Llamadas LLM | Temperature | Max Tokens |
|---|---|---|---|
| Chat | 1 | 0.7 | 512 |
| Board Room | 4 concurrentes | 0.6 | 512 cada uno |
| Diagnóstico | 1 | 0.5 | 1024 |
| Recomendaciones | 1 | 0.5 | 1536 |
| Gate Review | **0** | — | — |

### 9.4 Normalización de Respuestas

Todas las respuestas LLM pasan por `normalize.py`:

```python
normalize_string()           # Any -> str
normalize_list()             # Any -> list[str]
normalize_vote()             # Any -> "PROCEED" | "PIVOT" | "STOP"
normalize_confidence()       # Any -> float 0-100
normalize_analysis_response() # Normalización completa de análisis
```

---

## 10. Board Room — Sistema Multi-Agente

4 agentes independientes ejecutados **concurrentemente** (via `asyncio.gather`):

| Agente | Enfoque | System Prompt |
|---|---|---|
| CEO | Viabilidad general: visión, liderazgo, oportunidad | Español, ~50 tokens |
| CTO | Viabilidad técnica: factibilidad, riesgos, tecnología | Español, ~50 tokens |
| CFO | Viabilidad financiera: costos, ingresos, sostenibilidad | Español, ~50 tokens |
| CMO | Propuesta de valor: dolor real, demanda, diferenciación | Español, ~50 tokens |

**Cada agente produce:** analysis, justification, vote (PROCEED/PIVOT/STOP), confidence (0-100), key_strengths[], key_concerns[], questions[]

**Consenso:** Voto mayoritario con score ponderado. Registra disenso cuando algún agente discrepa.

**Rendimiento:** ~23s para los 4 agentes concurrentemente.

---

## 11. Gate Review — Scoring Determinístico

**7 criterios ponderados, 0 llamadas a LLM:**

| Criterio | Peso | Método de Evaluación |
|---|---|---|
| Claridad del Problema | 20% | Longitud diagnóstico + presencia keywords + profundidad conversación |
| Calidad de Evidencia | 20% | Datos cuantitativos + términos mercado + sustancia mensajes usuario |
| Validación de Mercado | 15% | Indicadores mercado + conciencia competencia + validación clientes |
| Viabilidad de Solución | 15% | Ratios voto Board Room + confianza promedio |
| Factibilidad Financiera | 10% | Términos financieros + modelo de precios + números en conversación |
| Alineación del Board | 10% | Ratio de voto PROCEED |
| Completitud de Entregables | 10% | Existencia diagnóstico + scores + documentos + conversación |

**Umbral:** 80/100 para aprobar. También requiere cero issues bloqueantes.

---

## 12. Gemelo Digital

El `GemeloDigitalService` persiste el estado completo:

| Función | Propósito |
|---|---|
| `get_or_create_project()` | 1:1 con company |
| `get_or_create_level()` / `activate_level()` / `complete_level()` | Ciclo de vida de niveles |
| `save_diagnosis()` | Documento con evento |
| `save_board_room_result()` | Decisión con evento |
| `save_score()` | Score con evento |
| `save_recommendation()` | Documento con evento |
| `get_gemelo_state()` | Snapshot de estado completo |

**Cada cambio genera un Event append-only.**

### 12.1 Los 7 Niveles

1. El Dolor (The Pain)
2. Propuesta de Valor (Value Proposition)
3. Plan de Negocios (Business Plan)
4. MVP
5. Validación Simulada (Simulated Validation)
6. Lanzamiento (Launch)
7. Escalamiento (Scaling)

---

## 13. Métricas Finales

### 13.1 Performance

| Operación | Tiempo |
|---|---|
| Chat | 4.23s |
| Board Room | 23.43s |
| Diagnóstico | 14.78s |
| Gate Review | 0.04s |
| **TOTAL Flujo Nivel 1** | **42.47s** |

**Target <45s: ALCANZADO**

### 13.2 Production Readiness

| Área | % | Justificación |
|---|---|---|
| Arquitectura | 95 | Estructura limpia, capas bien definidas |
| Docker | 95 | 4 contenedores, healthcheck, modelo auto |
| Backend | 90 | FastAPI completo, JWT, 11 modelos, 3 routers |
| Frontend | 80 | React funcional, 4 páginas |
| Ollama | 95 | Integración completa, adaptador desacoplado |
| Persistencia | 85 | SQLite WAL, 11 tablas, Gemelo Digital |
| Board Room | 90 | 4 agentes concurrentes con análisis real |
| Gate Review | 95 | Determinístico, 7 criterios, 0 LLM calls |
| Gemelo Digital | 85 | Persiste todo, cada cambio genera evento |
| Testing | 85 | 36 tests, 8 módulos, stress test |
| Seguridad | 65 | JWT + bcrypt + CORS |
| Performance | 90 | Nivel 1 en 42s (<45s target) |
| **Global** | **90** | **Nivel 1 funcional de extremo a extremo** |

---

## 14. Cobertura de Pruebas

### 14.1 Suite de Pruebas (36 tests, 8 módulos)

| Módulo | Tests | Estado |
|---|---|---|
| Auth | 7 | PASS |
| Companies | 5 | PASS |
| Models | 3 | PASS |
| Board Room | 5 | PASS |
| Gemelo Digital | 7 | PASS |
| Gate Review | 7 | PASS |
| Stress | 2 | PASS |
| **Total** | **36** | **36/36 PASS** |

### 14.2 Infraestructura de Tests

- In-memory SQLite con `StaticPool`
- Sesiones frescas por test
- `TestClient` con dependency override
- aiohttp para tests de estrés (requiere servidor corriendo)

### 14.3 Stress Tests

| Test | Usuarios | Resultado |
|---|---|---|
| Registros concurrentes | 10 | PASS |
| Board Room concurrente | 5 | PASS |

---

## 15. Frontend

### 15.1 Páginas

| Página | Ruta | Descripción |
|---|---|---|
| LoginPage | `/login` | Formulario email/password |
| RegisterPage | `/register` | Formulario name/email/password |
| DashboardPage | `/dashboard` | Grid de empresas, modal de creación, maturity display |
| Nivel1Page | `/nivel1/:companyId` | Vista con tabs: Chat, Board Room, Diagnosis, Scores |

### 15.2 Design System

- Tema oscuro con colores Tailwind personalizados (`adan-bg: #0f172a`, `adan-surface: #1e293b`, `adan-accent: #3b82f6`)
- Idioma español en toda la UI
- Chat con renderizado optimista de mensajes
- Diagnóstico renderiza Markdown via `react-markdown`

### 15.3 API Client

Clase `ApiClient` con gestión de token JWT, todos los métodos API mapeados, persistencia en localStorage.

### 15.4 Vite Config

Proxy: `/api` → `http://backend:8000` (para networking Docker)

---

## 16. Limitaciones Conocidas

1. **Sin GPU:** Ollama ejecuta en CPU only, impactando tiempos de respuesta
2. **Sin migrations:** Schema creado con `create_all()`, sin Alembic
3. **Sin rate limiting:** Sin protección contra abuso de API
4. **Streaming parcial:** SSE parcialmente implementado en chat
5. **Memoria entre sesiones:** Solo resumen básico, sin contexto persistente entre sesiones
6. **SQLite:** No escala a múltiples instancias o alto concurrencia
7. **Modelo pequeño:** Qwen 2.5:0.5b tiene calidad limitada para análisis complejos
8. **Tests de integración:** Faltan tests end-to-end del flujo completo
9. **Docker sin multi-stage:** Builds no optimizados para tamaño final
10. **Sin health check frontend:** Solo Ollama tiene healthcheck configurado

---

## 17. Riesgos Conocidos

1. **Seguridad:** Sin rate limiting, sin input validation avanzada, sin HTTPS en dev
2. **Escalabilidad:** SQLite no soporta concurrencia alta
3. **Dependencia Ollama:** Si Ollama no está disponible, el sistema completo falla
4. **Modelo pequeño:** Qwen 0.5b puede dar respuestas de baja calidad en casos complejos
5. **Sin backup:** No hay estrategia de backup automática para la BD
6. **JWT Secret:** Default secret en desarrollo, riesgo si se usa en producción
7. **CORS amplio:** Permite múltiples orígenes en desarrollo
8. **Sin logging centralizado:** Logs en JSON pero sin agregación

---

## 18. Documentación de Referencia

- `docs/WO-000_EXECUTIVE_ARCHITECTURE_SUMMARY.md` — Resumen ejecutivo de arquitectura
- `docs/WO-001_CIERRE_DEFINITIVO.md` — Cierre definitivo WO-001
- `docs/WO-001A_AUDITORIA_TECNICA.md` — Auditoría técnica
- `docs/ADR-001-Vertical-Nivel-1.md` — Architecture Decision Record
- `docs/wo-000/` — Especificaciones funcionales y fundamentos del dominio

---

**Este baseline está CONGELADO.**  
**Cualquier modificación requiere una Work Order específica.**  
**Ninguna WO futura podrá modificar la WO-001.**
