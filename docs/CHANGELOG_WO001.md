# CHANGELOG — WO-001

**Work Order:** WO-001  
**Fecha Inicio:** 2026-07-22  
**Fecha Cierre:** 2026-07-23  
**Estado:** CERRADA (90%)  
**Objetivo:** Nivel 1 completamente funcional con `docker compose up`

---

## Resumen Ejecutivo

WO-001 transformó ADÁN de un concepto arquitectónico a un sistema funcionando de extremo a extremo. Se construyó el backend completo, el frontend funcional, la integración con Ollama, el sistema multi-agente Board Room, el Gate Review determinístico, y el Gemelo Digital con persistencia total.

**Resultado:** 36 tests passing, flujo completo Nivel 1 en 42.47s (target <45s), 4 agentes concurrentes, 0 crash en stress test.

---

## Arquitectura

| Cambio | Descripción |
|---|---|
| Estructura de directorios | Creación de la estructura completa: `backend/app/{api,core,models,schemas,ai,nivel1,services}` |
| Contrato Base (AD-006) | Implementación del patrón base para todas las entidades: UUID, version, status, timestamps, confidence_level |
| Patrón Adapter para IA | Capa desacoplada `ai/base.py` con ABC `LLMAdapter` + factory registry |
| Append-only Events | Tabla Events como log inmutable de todos los cambios del sistema |
| Separación por capas | Backend organizado en: core, models, schemas, api, ai, nivel1, services |

---

## Backend

### API Endpoints

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/v1/auth/register` | POST | Registro de usuario con JWT |
| `/api/v1/auth/login` | POST | Login con JWT |
| `/api/v1/auth/me` | GET | Perfil del usuario actual |
| `/api/v1/companies/` | POST | Crear empresa (auto-crea Project + 7 Levels) |
| `/api/v1/companies/` | GET | Listar empresas del usuario |
| `/api/v1/companies/{id}` | GET | Obtener empresa |
| `/api/v1/companies/{id}/project` | GET | Obtener proyecto |
| `/api/v1/nivel1/{id}/status` | GET | Estado completo Nivel 1 |
| `/api/v1/nivel1/{id}/chat` | POST | Chat con IA |
| `/api/v1/nivel1/{id}/chat-stream` | POST | Chat con streaming SSE |
| `/api/v1/nivel1/{id}/board-room` | POST | Ejecutar Board Room |
| `/api/v1/nivel1/{id}/diagnosis` | POST | Generar diagnóstico |
| `/api/v1/nivel1/{id}/recommendations` | POST | Generar recomendaciones |
| `/api/v1/nivel1/{id}/gate-review` | POST | Ejecutar Gate Review |
| `/api/v1/nivel1/{id}/scores` | GET | Obtener scores |
| `/api/v1/nivel1/{id}/documents` | GET | Obtener documentos |
| `/health` | GET | Health check |
| `/` | GET | Info de la app |

### Modelos SQLAlchemy (11 tablas)

| Modelo | Tabla |
|---|---|
| User | users |
| Company | companies |
| FoundingNarrative | founding_narratives |
| Project | projects |
| Level | levels |
| Card | cards |
| Conversation | conversations |
| Message | messages |
| Score | scores |
| Decision | decisions |
| Document | documents |
| Event | events |

### Schemas Pydantic (15 schemas)

| Schema | Tipo |
|---|---|
| UserRegister | Request |
| UserLogin | Request |
| TokenResponse | Response |
| UserResponse | Response |
| CompanyCreate | Request |
| CompanyResponse | Response |
| ProjectResponse | Response |
| LevelResponse | Response |
| CardResponse | Response |
| ConversationResponse | Response |
| MessageCreate | Request |
| MessageResponse | Response |
| ScoreResponse | Response |
| DecisionResponse | Response |
| ChatRequest | Request |
| ChatResponse | Response |
| DashboardResponse | Response |
| GateReviewRequest | Request |
| GateReviewResponse | Response |

### Autenticación

- JWT con python-jose
- bcrypt para hashing de passwords
- Tokens de 24h de expiración
- Middleware de auth para endpoints protegidos

### Base de Datos

- SQLite con WAL mode
- Foreign keys habilitadas
- 11 tablas con relaciones completas
- Schema creation via `Base.metadata.create_all()`

---

## Frontend

### Páginas

| Página | Ruta | Funcionalidad |
|---|---|---|
| LoginPage | `/login` | Formulario email/password con redirección |
| RegisterPage | `/register` | Formulario name/email/password |
| DashboardPage | `/dashboard` | Grid de empresas, modal de creación, maturity display |
| Nivel1Page | `/nivel1/:companyId` | 4 tabs: Chat, Board Room, Diagnosis, Scores |

### Componentes

- `ApiClient` class con JWT management y localStorage
- `react-router-dom` para routing
- `react-markdown` para renderizado de diagnósticos
- Tailwind CSS con paleta de colores personalizada ADÁN
- Tema oscuro con scrollbars personalizados

### Diseño

- Colores: `adan-bg: #0f172a`, `adan-surface: #1e293b`, `adan-accent: #3b82f6`
- Idioma español en toda la UI
- Chat con renderizado optimista de mensajes

---

## Docker

### docker-compose.yml

| Servicio | Imagen | Puerto | Propósito |
|---|---|---|---|
| backend | Build `./backend` | 8050:8000 | FastAPI backend |
| frontend | Build `./frontend` | 5174:5173 | React/Vite dev server |
| ollama | `ollama/ollama:latest` | 11434:11434 | LLM inference |
| model-pull | `curlimages/curl:latest` | — | Init container para modelo |

### Volúmenes

- `backend-data`: Datos SQLite
- `ollama-models`: Pesos del modelo

### Healthcheck

- Ollama: TCP check en puerto 11434
- Backend: depends_on Ollama healthy + model-pull success

### Dockerfiles

- Backend: Python 3.12-slim, curl, pip deps, start.sh (espera Ollama, ejecuta uvicorn)
- Frontend: Node 20-slim, npm install, npm run dev

---

## IA

### Capa de IA

- **Patrón Adapter:** `LLMAdapter` ABC con `OllamaAdapter` implementado
- **Factory:** `get_llm_adapter()` lee `LLM_PROVIDER` del env
- **Normalización:** `normalize.py` garantiza contrato de datos único
- **Modelo:** Qwen 2.5:0.5b (Q4_K_M, 379.4 MB, CPU only)

### Board Room (Multi-Agente)

| Agente | Enfoque | Temperatura | Max Tokens |
|---|---|---|---|
| CEO | Viabilidad general | 0.6 | 512 |
| CTO | Viabilidad técnica | 0.6 | 512 |
| CFO | Viabilidad financiera | 0.6 | 512 |
| CMO | Propuesta de valor | 0.6 | 521 |

- **Ejecución:** Concurrente via `asyncio.gather`
- **Tiempo:** 23.43s para 4 agentes (vs ~34s secuencial anterior)
- **Consenso:** Voto mayoritario con score ponderado
- **Detección de disenso:** Registra cuando algún agente discrepa

### Gate Review (Determinístico)

- **0 llamadas a LLM**
- 7 criterios ponderados
- Umbral: 80/100
- Cálculo determinístico: `Score = Σ(criterio × peso)`

### Uso de IA por Punto

| Punto | Llamadas | Temperature | Max Tokens |
|---|---|---|---|
| Chat | 1 | 0.7 | 512 |
| Board Room | 4 | 0.6 | 512 c/u |
| Diagnóstico | 1 | 0.5 | 1024 |
| Recomendaciones | 1 | 0.5 | 1536 |
| Gate Review | 0 | — | — |

---

## Persistencia

### Gemelo Digital

| Función | Propósito |
|---|---|
| `get_or_create_project()` | 1:1 con company |
| `get_or_create_level()` | Obtener/crear nivel |
| `activate_level()` | Activar nivel siguiente |
| `complete_level()` | Completar nivel actual |
| `save_diagnosis()` | Guardar documento + evento |
| `save_board_room_result()` | Guardar decisión + evento |
| `save_score()` | Guardar score + evento |
| `save_recommendation()` | Guardar documento + evento |
| `get_gemelo_state()` | Snapshot completo |

### Eventos

- Tabla `events` append-only
- Cada cambio genera un evento con: event_type, entity_type, entity_id, data (JSON)
- Tipos de evento: level_activated, level_completed, diagnosis_saved, board_room_saved, score_saved, recommendation_saved

### Records (ejemplo de estado típico)

| Entidad | Registros |
|---|---|
| Users | 12+ |
| Companies | 12+ |
| Levels | 84+ (12 × 7) |
| Cards | 9+ |
| Conversations | 9+ |
| Messages | 22+ |
| Scores | 4+ |
| Documents | 4+ |
| Decisions | 14+ |
| Events | 24+ |

---

## Board Room

### Implementación

- 4 agentes independientes: CEO, CTO, CFO, CMO
- Cada uno recibe: contexto de la empresa, historial de chat, prompt específico
- Cada uno produce: analysis, justification, vote, confidence, key_strengths, key_concerns, questions
- Consenso: voto mayoritario con score ponderado
- Detección de disenso: registra cuando algún agente vota diferente

### Optimización

| Métrica | Antes | Después |
|---|---|---|
| Ejecución | Secuencial (for + await) | Concurrente (asyncio.gather) |
| Prompts | ~200 tokens | ~50 tokens |
| Tiempo | ~34s | 23.43s |

---

## Gate Review

### Implementación

- 0 llamadas a LLM
- 7 criterios con pesos que suman 1.0
- Evaluación basada en: longitud diagnóstico, presencia keywords, datos cuantitativos, votos Board Room, existencia documentos
- Umbral: 80/100 para aprobación
- Requiere cero issues bloqueantes

### Criterios

| Criterio | Peso |
|---|---|
| Claridad del Problema | 20% |
| Calidad de Evidencia | 20% |
| Validación de Mercado | 15% |
| Viabilidad de Solución | 15% |
| Factibilidad Financiera | 10% |
| Alineación del Board | 10% |
| Completitud de Entregables | 10% |

---

## Testing

### Suite Completa (36 tests)

| Módulo | Tests | Archivo |
|---|---|---|
| Auth | 7 | test_auth.py |
| Companies | 5 | test_companies.py |
| Models | 3 | test_models.py |
| Board Room | 5 | test_board_room.py |
| Gemelo Digital | 7 | test_gemelo_digital.py |
| Gate Review | 7 | test_gate_review.py |
| Stress | 2 | test_stress.py |

### Infraestructura

- In-memory SQLite con `StaticPool`
- Sesiones frescas por test
- `TestClient` con dependency override
- aiohttp para stress tests

### Stress Tests

| Test | Configuración | Resultado |
|---|---|---|
| Registros concurrentes | 10 usuarios | PASS |
| Board Room concurrente | 5 instancias | PASS |

---

## Performance

### Optimizaciones Implementadas

| Operación | Antes | Después | Mejora |
|---|---|---|---|
| Chat | 5.62s | 4.23s | -25% |
| Board Room | 33.89s | 23.43s | -31% |
| Diagnóstico | 79.33s | 14.78s | -81% |
| Gate Review | 25.61s | 0.04s | -99.8% |
| **TOTAL** | **144.45s** | **42.47s** | **-71%** |

### Target

- **<45s para flujo completo Nivel 1:** ALCANZADO (42.47s)

### Optimizaciones Clave

1. Board Room: secuencial → concurrente (asyncio.gather)
2. Prompts: ~200 tokens → ~50 tokens por agente
3. Gate Review: LLM-based → determinístico (0 llamadas LLM)
4. Diagnóstico: optimización de prompts y procesamiento

---

## Documentación

| Documento | Contenido |
|---|---|
| WO-000_EXECUTIVE_ARCHITECTURE_SUMMARY.md | Resumen ejecutivo de arquitectura |
| WO-001_CIERRE_DEFINITIVO.md | Cierre definitivo con métricas |
| WO-001A_AUDITORIA_TECNICA.md | Auditoría técnica detallada |
| ADR-001-Vertical-Nivel-1.md | Architecture Decision Record |
| WO-000_INDICE_MAESTRO_v1..v3.21.md | 21 versiones del índice maestro |
| docs/wo-000/ | Especificaciones funcionales y fundamentos |

---

## WO-002 — Congelación

Con el cierre de WO-001, se ejecuta WO-002 para:

1. Congelar el baseline oficial del Nivel 1
2. Documentar el changelog completo
3. Registrar deuda técnica
4. Definir suite de regresión
5. Congelar interfaces públicas

**Regla:** A partir de WO-002, ningún componente del Nivel 1 puede modificarse sin Work Order específica.

---

## Cierre

**WO-001 queda oficialmente CERRADA.**

El Nivel 1 de ADÁN funciona completamente de extremo a extremo:
- docker compose up → sistema arranca
- Registro → JWT auth
- Crear empresa → persistencia
- Chat → IA responde
- Board Room → 4 agentes concurrentes
- Diagnóstico → documento generado
- Gate Review → score determinístico 84/100
- Gemelo Digital → todo persistido
- Nivel completado → transición automática

**Los 10% restantes son mejoras de calidad (streaming, memoria, rate limiting) que no bloquean la funcionalidad del producto y quedan registrados en TECH_DEBT.md.**
