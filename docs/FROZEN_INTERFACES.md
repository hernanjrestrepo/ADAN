# FROZEN_INTERFACES — Interfaces Públicas Congeladas ADÁN Nivel 1

**Fecha de Congelación:** 2026-07-24  
**WO de Origen:** WO-001 (Cerrada)  
**Estado:** CONGELADO — Cualquier cambio incompatible requiere nueva Work Order

---

## Regla

**A partir de este momento, cualquier cambio incompatible en las interfaces documentadas aquí deberá pasar por una Work Order específica.**

Un cambio es **incompatible** si:
- Elimina un campo existente
- Renombra un campo existente
- Cambia el tipo de un campo existente
- Cambia el comportamiento semántico de un endpoint
- Agrega campos requeridos a requests existentes
- Cambia el formato de una respuesta

Un cambio es **compatible** si:
- Agrega campos opcionales a responses
- Agrega nuevos endpoints
- Agrega nuevos valores a enums (sin eliminar existentes)
- Agrega nuevas query parameters opcionales

Los cambios compatibles NO requieren Work Order.

---

## 1. APIs REST

### 1.1 Base URL

```
/api/v1
```

### 1.2 Autenticación

**Header:** `Authorization: Bearer <jwt_token>`

**Formato JWT:**
```json
{
  "sub": "<user_id>",
  "exp": <unix_timestamp>
}
```

### 1.3 Respuestas de Error

**Formato estándar:**
```json
{
  "detail": "<error_message>"
}
```

**Códigos de error comunes:**
| Código | Significado |
|---|---|
| 400 | Bad Request (datos inválidos) |
| 401 | Unauthorized (sin token o token inválido) |
| 403 | Forbidden (sin permisos) |
| 404 | Not Found (recurso no existe) |
| 422 | Unprocessable Entity (validación fallida) |
| 500 | Internal Server Error |

---

## 2. Contratos JSON Congelados

### 2.1 Auth

#### POST `/api/v1/auth/register`

**Request:**
```json
{
  "email": "string (required, email format)",
  "name": "string (required)",
  "password": "string (required, min 6 chars)"
}
```

**Response 201:**
```json
{
  "access_token": "string (JWT)",
  "token_type": "bearer",
  "user": {
    "id": "string (UUID)",
    "email": "string",
    "name": "string",
    "role": "user | primary_user"
  }
}
```

#### POST `/api/v1/auth/login`

**Request:**
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

**Response 200:**
```json
{
  "access_token": "string (JWT)",
  "token_type": "bearer",
  "user": {
    "id": "string (UUID)",
    "email": "string",
    "name": "string",
    "role": "user | primary_user"
  }
}
```

#### GET `/api/v1/auth/me`

**Response 200:**
```json
{
  "id": "string (UUID)",
  "email": "string",
  "name": "string",
  "role": "user | primary_user"
}
```

---

### 2.2 Companies

#### POST `/api/v1/companies/`

**Request:**
```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "industry": "string (optional)",
  "country": "string (optional)"
}
```

**Response 201:**
```json
{
  "id": "string (UUID)",
  "name": "string",
  "description": "string",
  "industry": "string",
  "country": "string",
  "maturity": "number (0.0 - 1.0)",
  "status": "active | archived",
  "version": "number (integer)",
  "created_at": "string (ISO 8601)"
}
```

**Side effects:**
- Crea automáticamente un `Project` asociado
- Crea 7 `Level`s (numbered 1-7)
- Crea un `FoundingNarrative` vacío

#### GET `/api/v1/companies/`

**Response 200:**
```json
[
  {
    "id": "string (UUID)",
    "name": "string",
    "description": "string",
    "industry": "string",
    "country": "string",
    "maturity": "number (0.0 - 1.0)",
    "status": "active | archived",
    "version": "number (integer)",
    "created_at": "string (ISO 8601)"
  }
]
```

#### GET `/api/v1/companies/{id}`

**Response 200:** (mismo formato que POST response)

#### GET `/api/v1/companies/{id}/project`

**Response 200:**
```json
{
  "id": "string (UUID)",
  "company_id": "string (UUID)",
  "name": "string",
  "status": "active | archived",
  "version": "number (integer)",
  "created_at": "string (ISO 8601)"
}
```

---

### 2.3 Nivel 1

#### GET `/api/v1/nivel1/{id}/status`

**Response 200:**
```json
{
  "company": {
    "id": "string (UUID)",
    "name": "string",
    "description": "string",
    "industry": "string",
    "country": "string",
    "maturity": "number (0.0 - 1.0)"
  },
  "project": {
    "id": "string (UUID)",
    "name": "string"
  },
  "current_level": {
    "id": "string (UUID)",
    "number": "number (1-7)",
    "name": "string",
    "status": "blocked | active | completed"
  },
  "scores": [
    {
      "id": "string (UUID)",
      "score_type": "problem | solution | business | product | market | execution",
      "value": "number (0-100)",
      "confidence_level": "number (0-100)",
      "reasoning": "string",
      "created_at": "string (ISO 8601)"
    }
  ],
  "recent_decisions": [
    {
      "id": "string (UUID)",
      "title": "string",
      "description": "string",
      "proposed_by": "string",
      "status": "proposed | approved | rejected | executed",
      "reasoning": "string",
      "confidence_level": "number (0-100)",
      "created_at": "string (ISO 8601)"
    }
  ],
  "progress": "number (0.0 - 1.0)"
}
```

#### POST `/api/v1/nivel1/{id}/chat`

**Request:**
```json
{
  "message": "string (required)",
  "conversation_id": "string (UUID, optional)"
}
```

**Response 200:**
```json
{
  "message": {
    "id": "string (UUID)",
    "conversation_id": "string (UUID)",
    "role": "user | assistant",
    "agent_name": "string | null",
    "content": "string",
    "created_at": "string (ISO 8601)"
  },
  "conversation_id": "string (UUID)",
  "card_id": "string (UUID)"
}
```

#### POST `/api/v1/nivel1/{id}/chat-stream`

**Response 200:** (SSE stream)

**Formato SSE:**
```
data: {"content": "string chunk"}

data: {"content": "string chunk"}

data: [DONE]
```

#### POST `/api/v1/nivel1/{id}/board-room`

**Response 200:**
```json
{
  "consensus": {
    "vote": "PROCEED | PIVOT | STOP",
    "score": "number (0-100)",
    "summary": "string"
  },
  "votes": [
    {
      "agent": "CEO | CTO | CFO | CMO",
      "vote": "PROCEED | PIVOT | STOP",
      "confidence": "number (0-100)",
      "analysis": "string",
      "justification": "string",
      "key_strengths": ["string"],
      "key_concerns": ["string"],
      "questions": ["string"]
    }
  ],
  "dissent": "boolean",
  "execution_time": "number (seconds)"
}
```

#### POST `/api/v1/nivel1/{id}/diagnosis`

**Response 200:**
```json
{
  "document": {
    "id": "string (UUID)",
    "title": "string",
    "content": "string (markdown)",
    "doc_type": "diagnosis",
    "origin": "generated_by_adan",
    "created_at": "string (ISO 8601)"
  }
}
```

#### POST `/api/v1/nivel1/{id}/recommendations`

**Response 200:**
```json
{
  "document": {
    "id": "string (UUID)",
    "title": "string",
    "content": "string (markdown)",
    "doc_type": "recommendations",
    "origin": "generated_by_adan",
    "created_at": "string (ISO 8601)"
  }
}
```

#### POST `/api/v1/nivel1/{id}/gate-review`

**Request:**
```json
{
  "level_number": "number (1-7, optional)"
}
```

**Response 200:**
```json
{
  "approved": "boolean",
  "score": "number (0-100)",
  "criteria": [
    {
      "name": "string",
      "weight": "number (0.0 - 1.0)",
      "score": "number (0-100)",
      "reasoning": "string"
    }
  ],
  "blocking_issues": ["string"],
  "recommendations": ["string"],
  "level_status": "blocked | active | completed",
  "message": "string"
}
```

#### GET `/api/v1/nivel1/{id}/scores`

**Response 200:**
```json
[
  {
    "id": "string (UUID)",
    "project_id": "string (UUID)",
    "score_type": "problem | solution | business | product | market | execution",
    "value": "number (0-100)",
    "confidence_level": "number (0-100)",
    "reasoning": "string",
    "evidence": "object | null",
    "created_at": "string (ISO 8601)"
  }
]
```

#### GET `/api/v1/nivel1/{id}/documents`

**Response 200:**
```json
[
  {
    "id": "string (UUID)",
    "title": "string",
    "content": "string",
    "doc_type": "diagnosis | recommendations | other",
    "origin": "generated_by_adan | received_from_client",
    "created_at": "string (ISO 8601)"
  }
]
```

---

## 3. Eventos

### 3.1 Formato de Evento

```json
{
  "id": "string (UUID)",
  "project_id": "string (UUID)",
  "event_type": "string",
  "entity_type": "string",
  "entity_id": "string (UUID)",
  "data": "object (JSON)",
  "created_at": "string (ISO 8601)"
}
```

### 3.2 Tipos de Evento Congelados

| event_type | entity_type | data esperado |
|---|---|---|
| `level_activated` | `level` | `{ level_number, level_name }` |
| `level_completed` | `level` | `{ level_number, level_name, completed_at }` |
| `diagnosis_saved` | `document` | `{ document_id, title }` |
| `board_room_saved` | `decision` | `{ decision_id, title, vote, confidence }` |
| `score_saved` | `score` | `{ score_id, score_type, value }` |
| `recommendation_saved` | `document` | `{ document_id, title }` |
| `chat_message` | `message` | `{ message_id, role, content_preview }` |

---

## 4. Modelos de Datos

### 4.1 Enums Congelados

| Enum | Valores |
|---|---|
| `EntityStatus` | `active`, `archived` |
| `UserRole` | `user`, `primary_user` |
| `NivelStatus` | `blocked`, `active`, `completed` |
| `CardStatus` | `blocked`, `active`, `completed` |
| `DecisionStatus` | `proposed`, `approved`, `rejected`, `executed` |
| `ScoreType` | `problem`, `solution`, `business`, `product`, `market`, `execution` |

### 4.2 Contrato Base (todas las entidades)

```json
{
  "id": "string (UUID)",
  "version": "number (integer, default 1)",
  "status": "active | archived",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)",
  "created_by": "string (UUID, nullable)",
  "confidence_level": "number (0-100, nullable)"
}
```

---

## 5. Estructuras de Persistencia

### 5.1 Tablas Congeladas

| Tabla | Columnas Principales |
|---|---|
| `users` | id, email, name, hashed_password, role, created_at, updated_at |
| `companies` | id, name, description, industry, country, maturity, primary_user_id, status, version |
| `founding_narratives` | id, company_id, origin_story, founding_motivation, irreversible_commitment |
| `projects` | id, company_id, name, status, version, created_at |
| `levels` | id, project_id, number, name, status, completed_at |
| `cards` | id, project_id, level_id, title, description, card_type, status |
| `conversations` | id, card_id, title, summary, status, created_at |
| `messages` | id, conversation_id, role, agent_name, content, metadata_json, created_at |
| `scores` | id, project_id, score_type, value, confidence_level, reasoning, evidence, created_at |
| `decisions` | id, project_id, title, description, proposed_by, approved_by, status, reasoning, disagreement, confidence_level, created_at |
| `documents` | id, project_id, title, content, doc_type, origin, created_at |
| `events` | id, project_id, event_type, entity_type, entity_id, data, created_at |

### 5.2 Relaciones Congeladas

```
users 1:N companies
companies 1:1 founding_narratives
companies 1:N projects
projects 1:N levels
projects 1:N cards
projects 1:N scores
projects 1:N decisions
projects 1:N documents
projects 1:N events
levels 1:N cards
cards 1:N conversations
conversations 1:N messages
```

### 5.3 Índices

- `users.email` (unique)
- `companies.primary_user_id`
- `projects.company_id`
- `levels.project_id`
- `cards.project_id`
- `cards.level_id`
- `conversations.card_id`
- `messages.conversation_id`
- `scores.project_id`
- `decisions.project_id`
- `documents.project_id`
- `events.project_id`

---

## 6. Nombres de Niveles Congelados

| Número | Nombre | Nombre en Inglés |
|---|---|---|
| 1 | El Dolor | The Pain |
| 2 | Propuesta de Valor | Value Proposition |
| 3 | Plan de Negocios | Business Plan |
| 4 | MVP | MVP |
| 5 | Validación Simulada | Simulated Validation |
| 6 | Lanzamiento | Launch |
| 7 | Escalamiento | Scaling |

---

## 7. Agentes del Board Room Congelados

| Agente | Nombre | Enfoque |
|---|---|---|
| CEO | Director Ejecutivo | Viabilidad general, visión, liderazgo |
| CTO | Director Tecnológico | Viabilidad técnica, factibilidad, riesgos |
| CFO | Director Financiero | Viabilidad financiera, costos, ingresos |
| CMO | Director de Marketing | Propuesta de valor, demanda, diferenciación |

**Formato de voto:** `PROCEED` | `PIVOT` | `STOP`  
**Rango de confianza:** 0-100  
**Consenso:** Voto mayoritario con score ponderado

---

## 8. Criterios del Gate Review Congelados

| Criterio | Peso | Fuente |
|---|---|---|
| Claridad del Problema | 20% | Diagnóstico + conversación |
| Calidad de Evidencia | 20% | Datos cuantitativos + fuentes |
| Validación de Mercado | 15% | Competencia + clientes |
| Viabilidad de Solución | 15% | Votos Board Room |
| Factibilidad Financiera | 10% | Modelo de precios |
| Alineación del Board | 10% | Ratio PROCEED/STOP |
| Completitud de Entregables | 10% | Documentos + scores |

**Umbral de aprobación:** 80/100  
**Requisito adicional:** Cero issues bloqueantes

---

## 9. Variables de Entorno Congeladas

### 9.1 Backend

| Variable | Default | Tipo |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/adan.db` | string |
| `JWT_SECRET` | `adan-dev-secret-change-in-production` | string |
| `JWT_EXPIRATION_MINUTES` | `1440` | integer |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | string (URL) |
| `DEFAULT_MODEL` | `qwen2.5:0.5b` | string |
| `AI_TIMEOUT_SECONDS` | `120` | integer |
| `LLM_PROVIDER` | `ollama` | string (registry key) |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | string (comma-separated) |

### 9.2 Root

| Variable | Default | Tipo |
|---|---|---|
| `JWT_SECRET` | `adan-dev-secret-change-in-production` | string |
| `DEFAULT_MODEL` | `qwen2.5:0.5b` | string |

---

## 10. Puertos Congelados

| Servicio | Puerto Interno | Puerto Externo |
|---|---|---|
| Backend (FastAPI) | 8000 | 8050 |
| Frontend (Vite) | 5173 | 5174 |
| Ollama | 11434 | 11434 |

---

## 11. Design System Congelado

### 11.1 Paleta de Colores

| Token | Valor | Uso |
|---|---|---|
| `adan-bg` | `#0f172a` | Fondo principal |
| `adan-surface` | `#1e293b` | Superficies, cards |
| `adan-accent` | `#3b82f6` | Acentos, botones primarios |
| `adan-text` | `#e2e8f0` | Texto principal |
| `adan-muted` | `#94a3b8` | Texto secundario |

### 11.2 Fuentes

- **UI:** Sistema (sans-serif)
- **Markdown:** Monospace para código

### 11.3 Idioma

- **UI completa en español**
- **Mensajes de error en español**
- **Tooltips en español**

---

## 12. Acuerdos de Cambio

### 12.1 Cambios que Requieren Work Order

- Eliminar un endpoint existente
- Renombrar un endpoint existente
- Cambiar el método HTTP de un endpoint
- Eliminar un campo de un response
- Renombrar un campo de un response
- Cambiar el tipo de un campo existente
- Agregar campos requeridos a un request existente
- Cambiar el comportamiento semántico de un endpoint
- Modificar la lógica del Gate Review
- Modificar los agentes del Board Room
- Cambiar los pesos del Gate Review
- Modificar el modelo de persistencia

### 12.2 Cambios que NO Requieren Work Order

- Agregar campos opcionales a responses
- Agregar nuevos endpoints
- Agregar nuevos valores a enums (sin eliminar existentes)
- Agregar nuevas query parameters opcionales
- Agregar nuevas variables de entorno (con default)
- Agregar nuevos servicios internos
- Optimizar performance sin cambiar comportamiento
- Corregir bugs sin cambiar contrato

---

**Estas interfaces están CONGELADAS.**  
**Los cambios compatibles pueden implementarse directamente.**  
**Los cambios incompatibles requieren Work Order específica.**
