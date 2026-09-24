# TEST_BASELINE — Suite de Regresión Oficial ADÁN Nivel 1

**Fecha de Establecimiento:** 2026-07-24  
**WO de Origen:** WO-001 (Cerrada)  
**Estado:** CONGELADO — Suite oficial de regresión

---

## Regla

**Toda Work Order futura DEBE aprobar esta suite de pruebas antes de ser considerada completa.**

Si alguna prueba falla, la WO no puede cerrarse hasta que se resuelva.

---

## 1. Suite Unitaria (36 tests)

### 1.1 Auth (`test_auth.py` — 7 tests)

| # | Test | Descripción |
|---|---|---|
| 1 | `test_register_user` | Registro exitoso retorna JWT + user |
| 2 | `test_register_duplicate_email` | Email duplicado retorna error 400 |
| 3 | `test_login_success` | Login correcto retorna JWT |
| 4 | `test_login_wrong_password` | Password incorrecto retorna error 401 |
| 5 | `test_login_nonexistent_user` | Usuario inexistente retorna error 401 |
| 6 | `test_get_me_authenticated` | GET /me con token válido retorna perfil |
| 7 | `test_get_me_unauthenticated` | GET /me sin token retorna error 401 |

### 1.2 Companies (`test_companies.py` — 5 tests)

| # | Test | Descripción |
|---|---|---|
| 1 | `test_create_company` | Crear empresa retorna company + project + 7 levels |
| 2 | `test_list_companies` | Listar retorna empresas del usuario |
| 3 | `test_get_company` | Obtener empresa por ID |
| 4 | `test_get_company_not_found` | ID inexistente retorna 404 |
| 5 | `test_create_company_unauthenticated` | Sin token retorna 401 |

### 1.3 Models (`test_models.py` — 3 tests)

| # | Test | Descripción |
|---|---|---|
| 1 | `test_user_model` | Crear user en BD con campos correctos |
| 2 | `test_company_model` | Crear company con relationship a user |
| 3 | `test_level_model` | Crear 7 niveles para un project |

### 1.4 Board Room (`test_board_room.py` — 5 tests)

| # | Test | Descripción |
|---|---|---|
| 1 | `test_board_room_runs_all_agents` | 4 agentes ejecutan y producen voto |
| 2 | `test_board_room_returns_consensus` | Consenso mayoritario se produce |
| 3 | `test_board_room_concurrent_execution` | 4 agentes corren en <0.3s (concurrentes) |
| 4 | `test_board_room_vote_normalization` | Votos normalizados a PROCEED/PIVOT/STOP |
| 5 | `test_board_room_confidence_range` | Confianza entre 0 y 100 |

### 1.5 Gemelo Digital (`test_gemelo_digital.py` — 7 tests)

| # | Test | Descripción |
|---|---|---|
| 1 | `test_get_or_create_project` | Proyecto se crea o retorna existente |
| 2 | `test_get_or_create_level` | Nivel se crea o retorna existente |
| 3 | `test_activate_level` | Activar nivel siguiente funciona |
| 4 | `test_complete_level` | Completar nivel actualiza estado |
| 5 | `test_save_diagnosis` | Guardar diagnóstico crea documento + evento |
| 6 | `test_save_board_room_result` | Guardar resultado Board Room crea decisión + evento |
| 7 | `test_save_score` | Guardar score crea score + evento |

### 1.6 Gate Review (`test_gate_review.py` — 7 tests)

| # | Test | Descripción |
|---|---|---|
| 1 | `test_gate_review_deterministic` | Mismos inputs = mismo output |
| 2 | `test_gate_review_weights_sum_to_one` | Pesos suman 1.0 |
| 3 | `test_gate_review_score_range` | Score entre 0 y 100 |
| 4 | `test_gate_review_blocks_with_issues` | Issues bloqueantes previenen aprobación |
| 5 | `test_gate_review_approves_high_score` | Score >= 80 aprueba |
| 6 | `test_gate_review_rejects_low_score` | Score < 80 rechaza |
| 7 | `test_gate_review_no_llm_calls` | 0 llamadas a LLM (determinístico) |

### 1.7 Stress (`test_stress.py` — 2 tests)

| # | Test | Descripción | Requisito |
|---|---|---|---|
| 1 | `test_concurrent_registrations` | 10 registros concurrentes exitosos | Servidor corriendo |
| 2 | `test_concurrent_board_room` | 5 Board Rooms concurrentes exitosos | Servidor corriendo |

---

## 2. Suite de Integración (Requerida)

### 2.1 Flujo Completo Nivel 1

| # | Paso | Validación |
|---|---|---|
| 1 | POST /api/v1/auth/register | 201 + JWT |
| 2 | POST /api/v1/auth/login | 200 + JWT |
| 3 | POST /api/v1/companies/ | 201 + company + project + 7 levels |
| 4 | GET /api/v1/companies/ | 200 + lista incluye la empresa |
| 5 | GET /api/v1/companies/{id} | 200 + empresa correcta |
| 6 | GET /api/v1/companies/{id}/project | 200 + project correcto |
| 7 | GET /api/v1/nivel1/{id}/status | 200 + estado completo |
| 8 | POST /api/v1/nivel1/{id}/chat | 200 + respuesta IA |
| 9 | POST /api/v1/nivel1/{id}/board-room | 200 + 4 votos |
| 10 | POST /api/v1/nivel1/{id}/diagnosis | 200 + documento |
| 11 | POST /api/v1/nivel1/{id}/gate-review | 200 + score |
| 12 | GET /api/v1/nivel1/{id}/scores | 200 + scores |
| 13 | GET /api/v1/nivel1/{id}/documents | 200 + documentos |

### 2.2 Validaciones por Paso

| Paso | Códigos Esperados | Datos Esperados |
|---|---|---|
| Register | 201 | access_token, user.id, user.email |
| Login | 200 | access_token, user.id |
| Create Company | 201 | company.id, project.id, levels.length == 7 |
| List Companies | 200 | array con company.id |
| Get Company | 200 | company.name, company.industry |
| Get Project | 200 | project.company_id == company.id |
| Status | 200 | company, project, current_level, scores |
| Chat | 200 | message.content, message.role == "assistant" |
| Board Room | 200 | votes.length == 4, consensus |
| Diagnosis | 200 | document.content.length > 0 |
| Gate Review | 200 | score >= 0, score <= 100 |
| Scores | 200 | array de scores |
| Documents | 200 | array de documentos |

---

## 3. Comandos de Ejecución

### 3.1 Tests Unitarios

```bash
# Desde backend/
python -m pytest tests/ -v

# Output esperado:
# 36 passed in X.XXs
```

### 3.2 Tests de Stress (requieren servidor)

```bash
# Asegurar que el servidor esté corriendo
docker compose up -d

# Ejecutar stress tests
python -m pytest tests/test_stress.py -v

# Output esperado:
# 2 passed
```

### 3.3 Health Check

```bash
curl http://localhost:8050/health
# Expected: {"status": "healthy"}
```

### 3.4 Verificación de Endpoints

```bash
# Register
curl -X POST http://localhost:8050/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","name":"Test","password":"test123"}'

# Login
curl -X POST http://localhost:8050/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# Create Company (con token)
curl -X POST http://localhost:8050/api/v1/companies/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Company","description":"Test","industry":"tech","country":"US"}'
```

---

## 4. Criterios de Aprobación

### 4.1 Para Cerrar una Work Order

| Criterio | Requisito |
|---|---|
| Tests unitarios | 36/36 passing |
| Tests de stress | 2/2 passing |
| Health check | 200 OK |
| Flujo completo | Todos los endpoints responden correctamente |
| Regresión | Ningún test existente roto |

### 4.2 Para Aprobar un PR

| Criterio | Requisito |
|---|---|
| Tests unitarios | 100% passing |
| No-regresión | Ningún test existente falla |
| Coverage | No se reduce la cobertura existente |

---

## 5. Infraestructura de Tests

### 5.1 Configuración

- **Base de datos:** In-memory SQLite con `StaticPool`
- **Sesiones:** Frescas por test (rollback automático)
- **Cliente:** `TestClient` de FastAPI con dependency override
- **Fixtures:** Definidas en `conftest.py`

### 5.2 Fixtures Principales

| Fixture | Propósito |
|---|---|
| `db_session` | Sesión de BD en memoria |
| `client` | TestClient con DB override |
| `auth_headers` | Headers con JWT válido |
| `test_user` | Usuario de prueba creado |
| `test_company` | Empresa de prueba creada |

### 5.3 Ejecución CI

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar todos los tests
python -m pytest tests/ -v --tb=short

# Ejecutar con coverage
python -m pytest tests/ --cov=app --cov-report=term-missing
```

---

## 6. Mantenimiento de la Suite

### 6.1 Reglas

1. **No eliminar tests existentes** sin Work Order específica
2. **No modificar el comportamiento** de tests existentes
3. **Agregar tests** para nuevas funcionalidades es obligatorio
4. **Mantener la suite passing** es condición para cerrar cualquier WO

### 6.2 Ejecución Obligatoria

Antes de aprobar cualquier Work Order futura, se debe ejecutar:

```bash
python -m pytest tests/ -v
```

**Resultado esperado:** 36 passed, 0 failed

### 6.3 Documentar Nuevos Tests

Si una WO agrega tests, este documento debe actualizarse para incluir:
- Nombre del test
- Descripción
- Módulo al que pertenece

---

**Esta suite está CONGELADA.**  
**Las modificaciones deben pasar por una Work Order específica.**  
**Toda WO futura DEBE aprobar esta suite antes de cerrarse.**
