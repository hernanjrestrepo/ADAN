# Auditoría técnica de ADÁN — septiembre 2026

**Fecha:** 2026-09-24
**Alcance:** Build C (línea oficial) completa: `backend/app` (13.184 líneas, 90 archivos), `backend/tests` (4.597 líneas), `frontend/src` (940 líneas), Docker y scripts. Build A (`adan-platform/`) revisado a nivel de inventario para reutilización. Blueprint: `ADAN_Blueprint_v1.pdf`, `docs/wo-000/*`, `adan-platform/docs/blueprint/*`, `ADAN_MASTER_ARCHITECTURE_v1.0.md` y documentos de gobierno.
**Método:** lectura completa del código de Build C; ejecución real de pruebas (Python 3.12, Linux), del build del frontend y de `npm audit`; pruebas de explotación con dos usuarios contra la API levantada en memoria. Lo que no se ejecutó se dice explícitamente.
**Estado:** propuesta para revisión de Hernán (CTO). Este documento no se declara fuente de verdad (Regla 6 de `AD-GOV-0001`); el Canon sigue siendo `AD-ROOT-0001`.
**Plan derivado:** `docs/auditoria/PLAN_WO_ADAN_100.md`.

---

## 1. Qué es ADÁN

Un "Sistema Operativo Empresarial" con IA: acompaña a una empresa desde la idea hasta la operación a través de **7 Niveles** (El Dolor → Propuesta de Valor → Plan de Negocios → MVP → Validación Simulada → Lanzamiento → Escalamiento). En cada Nivel, un **Board Room** de agentes ejecutivos (CEO, CTO, CFO, CMO, Legal, Producto, Operaciones) delibera con el cliente, todo queda registrado en un **Gemelo Digital** de la empresa, y el avance entre Niveles se aprueba por **evidencia**, nunca por pago. Después de los 7 Niveles, la empresa pasa a operación continua por suscripción. Se integra con el ecosistema Paradixe: EVA (finanzas), ARQAI (voz), Genexis (construcción de software) y CSI (inteligencia de mercado).

## 2. Qué hay en el repositorio

| Ubicación | Qué es | Estado |
|---|---|---|
| Raíz (`backend/`, `frontend/`, `docs/`) | **Build C**: FastAPI + SQLite + React (JSX) + Ollama (`qwen2.5:0.5b`) | Línea oficial |
| `adan-platform/` | **Build A**: FastAPI + PostgreSQL/pgvector + Redis + React/TypeScript, WO-000 → WO-003 | Archivo histórico; fuente de reutilización |
| `autonomous/` | Prototipo 2024 en AWS (Lambda que se clona a sí misma) | Histórico, sin relación de código |
| — | **Build B** (rama `adan/platform-integration` del monorepo local, WO-000 → WO-012, tag `v1.0.0`) | Fuera de este repositorio; importación aprobada, pendiente |

---

## 3. Avance: ~22 % hacia ADÁN Enterprise v1

**Definición de 100 %:** los 7 Niveles funcionando de punta a punta según el blueprint (AD-FUNC-01 a 09), sobre una plataforma apta para producción (PostgreSQL, seguridad por empresa, CI/CD, observabilidad). Quedan fuera las reservas de negocio (WO-100) y de SaaS (WO-101 → 106), que requieren aprobación propia.

**Método:** cada componente tiene un peso según su importancia en el blueprint y un avance estimado a partir del código leído y ejecutado. Es una estimación razonada, no una medición; el valor útil es el orden de magnitud y dónde está el hueco.

### 3.1 Producto (peso 72)

| Componente | Peso | Avance | Evidencia |
|---|---:|---:|---|
| Los 7 Niveles (AD-FUNC-01) | 20 | 8 % | Solo Nivel 1 tiene lógica (~55 % de su especificación). Niveles 2–7 existen como filas `blocked` en la tabla `levels`, sin código |
| Board Room (AD-FUNC-02) | 6 | 35 % | Dos implementaciones distintas (4 agentes en paralelo en `nivel1/board_room.py`; 7 secuenciales en `agents/board.py`), ninguna con los 7 roles especificados; sin participación del cliente ni actas |
| Gemelo Digital (AD-007, AD-CMP-06) | 6 | 20 % | 11 de 38 entidades; los campos `version` nunca se incrementan; sin ciclo de vida (dividir, fusionar, archivar) |
| Frontend / UX (AD-UX) | 5 | 15 % | Login, registro, panel y pantalla de Nivel 1. No hay UI para EMS, TEF, Board de 7 agentes, OOS ni ningún otro Nivel |
| Onboarding (AD-FUNC-06) | 3 | 30 % | Registro y formulario de empresa. Sin identidad progresiva, multicanal, recuperación ni medición de los 30 s |
| Decisiones (AD-CMP-03, Patrón A) | 3 | 15 % | La tabla existe, pero el Board aprueba solo (`PROCEED` → `approved`); no hay endpoint para que el cliente apruebe o rechace |
| Scoring (AD-FUNC-07) | 3 | 10 % | 1 de 8 scores (Problem), calculado a partir de la "confianza" que declara el LLM |
| Motor de Estrategias (AD-FUNC-05) | 3 | 0 % | No existe |
| Learning Engine (AD-FUNC-09) | 3 | 5 % | Clase en memoria, sin persistencia ni API (`learning/engine.py`) |
| Memoria y contexto (AD-CMP-04) | 3 | 20 % | El chat reenvía todo el historial; los resúmenes nunca se generan; memoria de largo plazo vacía por diseño |
| EMS / Knowledge Graph | 3 | 30 % | Ingesta y hechos en BD; los embeddings son un hash de palabras (no semánticos) y el índice vectorial vive en memoria, uno por router |
| TEF (herramientas) | 2 | 35 % | Framework correcto. Herramientas: calculadora, HTTP y correo simulado; sin permisos, confirmaciones ni timeouts efectivos |
| OOS (operación continua) | 2 | 45 % | Modelo, servicios y API completos, pero sin endpoint para crear organizaciones ni UI |
| Experience Engine (AD-FUNC-03) | 2 | 0 % | No existe |
| Gamification Engine (AD-FUNC-04) | 2 | 0 % | No existe |
| Voz y omnicanal | 2 | 7 % | Adaptadores que responden éxito sin hacer nada (`voice/adapter.py`, `omnichannel/channels.py`) |
| Integraciones del ecosistema (EVA, ARQAI, Genexis, CSI) y conectores | 2 | 3 % | Conectores simulados que "se conectan" sin credenciales; ninguna integración con el ecosistema |
| DKA (adquisición de conocimiento) | 1 | 30 % | Scraping funcional de URLs dadas; la "búsqueda" son URLs fijas de demostración |
| Marketplace | 1 | 5 % | Clase en memoria sin API (`plugins/marketplace.py`) |
| **Subtotal producto** | **72** | **15 %** | |

### 3.2 Plataforma (peso 28)

| Componente | Peso | Avance | Evidencia |
|---|---:|---:|---|
| Backend, API y autenticación | 5 | 60 % | FastAPI ordenado, JWT + bcrypt; sin límite de intentos ni política de contraseñas |
| Datos | 5 | 25 % | SQLite, sin migraciones, tres bases declarativas separadas. El objetivo (PostgreSQL + pgvector) ya existe en Build A |
| IA | 4 | 30 % | Solo Ollama con un modelo de 0,5B; sin enrutamiento Haiku/Sonnet/Opus (AD-IA-01), reintentos ni medición de costo |
| Seguridad | 5 | 45 % | Tras WO-094. Pendiente: secreto JWT por defecto, token en `localStorage`, sin auditoría persistente ni límite de peticiones |
| Pruebas | 4 | 50 % | 230 pruebas, cobertura previa del 79 %; varias prueban esqueletos en memoria; sin pruebas de frontend ni CI |
| Producción (CI/CD, observabilidad, backups) | 5 | 15 % | Docker en modo desarrollo (`--reload`, servidor de Vite); sin CI/CD, métricas ni backups |
| **Subtotal plataforma** | **28** | **37 %** | |

**Total ponderado: ~22 %.** El vertical de Nivel 1 funciona de punta a punta en local, pero el resto del producto especificado todavía no existe o está simulado.

### 3.3 Avance del blueprint (documentación)

El índice maestro v3 define 58 documentos. Están escritos los 24 de la Fase 1 (Fundamentos, Comportamientos y Funcionalidades), es decir, **41 %**. AD-FUNC-07, 08 y 09, además de AD-003 v1.2 y AD-006 v1.2, solo existen en `adan-platform/docs/blueprint/`, no en `docs/wo-000/`. Faltan los 34 de la Fase 2: 12 de UX, 10 de Arquitectura, 4 de IA, 3 de Operación, 1 de Platform Services y 4 de Integraciones.

---

## 4. Evidencia ejecutada

| Verificación | Resultado |
|---|---|
| Suite backend (Python 3.12, Linux), antes de WO-094 | 201 pasan, 7 fallan: 5 de `test_board_room.py` por `asyncio.get_event_loop()` y 2 de `test_stress.py` porque necesitan el backend levantado |
| La hipótesis de WO-090 de que los 5 fallos eran exclusivos de Windows | **Refutada**: fallan igual en Linux con Python 3.12. El error es de la prueba, no del producto |
| Suite backend después de WO-094 | **228 pasan**; las 2 de `test_stress.py` pasan con el backend levantado en `:8050`. Total 230/230 |
| Build del frontend | Compila (201 módulos, 303 kB) |
| `npm audit` | **5 vulnerabilidades (3 moderadas, 2 altas)**: `nanoid` y `react-router`; en julio eran 4 |
| Stack completo con Docker y Ollama | No ejecutado en esta auditoría |

---

## 5. Hallazgos

Severidad: 🔴 crítica · 🟠 alta · 🟡 media · ⚪ baja.

### 5.1 Seguridad — corregidos en WO-094 (verificados con explotación real antes de corregir)

| # | Sev. | Hallazgo | Cómo se verificó |
|---|---|---|---|
| S1 | 🔴 | Ejecución remota de código: cualquier usuario registrado podía ejecutar Python en el servidor con `POST /tef/execute` y `python_sandbox`, que no tenía ningún aislamiento | Ejecutó `print(6*7)` usando un `company_id` inventado |
| S2 | 🔴 | La verificación de "empresa propia" en `/tef/execute` y `/tef/audit` nunca se ejecutaba, porque dependía de `executor.db`, que siempre era `None` | Igual que S1 |
| S3 | 🔴 | La calculadora usaba `eval` sin builtins, que se puede evadir: permitía importar `os` | Obtuvo `os.getcwd()` |
| S4 | 🟠 | `file_reader` leía cualquier archivo (`.env`, `/proc/self/environ`, la BD) | Leyó `/etc/hostname` |
| S5 | 🟠 | Un usuario podía leer los diagnósticos y scores de cualquier empresa (`/nivel1/{id}/documents` y `/scores` no verificaban la propiedad) | El usuario B leyó el diagnóstico privado de A |
| S6 | 🟠 | Un usuario podía escribir en la conversación de otro y hacer que la IA le devolviera su contenido (`conversation_id` sin verificar en chat, chat-stream y cognitivo) | La respuesta a B contenía el "secreto comercial" que había escrito A |
| S7 | 🟠 | Todo el módulo OOS (Work Orders, KPIs, riesgos, reuniones, dashboard) era accesible entre empresas | B listó las Work Orders de la organización de A |
| S8 | 🟠 | SSRF: `http_request`, `/dka/acquire` (con URLs del usuario) y el conector REST podían pedir direcciones internas (metadatos de la nube, Ollama, localhost); DKA además guardaba la respuesta en la memoria de la empresa | Revisión de código; pruebas de bloqueo en `tests/test_security.py` |
| S9 | 🟡 | La memoria de corto plazo del sistema cognitivo leía conversaciones de todas las empresas | Revisión de código |
| S10 | 🟡 | `/ems/correct` podía modificar la confianza de hechos de otra empresa | Revisión de código |
| S11 | 🟡 | `sql_query` (no registrada, pero disponible) permitía `SELECT` libre sobre la BD compartida, incluida `users.hashed_password`; además fallaba siempre con SQLAlchemy 2 porque faltaba `text()` | Ejecución directa |

**Riesgo residual:** la protección contra SSRF valida DNS antes de conectar, así que sigue expuesta a DNS rebinding. Se cierra con un proxy de salida en WO-097.

### 5.2 Seguridad — pendientes

*Actualización 2026-09-24:* WO-097 corrigió S12 a S16 y S17 en parte; WO-092 cerró S17 (`npm audit`: 0 vulnerabilidades, con vite 8 y react-router 8). S18 queda aceptado. Detalle en `docs/wo/WO-097_REPORTE.md`.

| # | Sev. | Hallazgo | Dónde |
|---|---|---|---|
| S12 | 🟠 | Si no se define `JWT_SECRET`, se usa un valor por defecto que ahora es público; con él cualquiera puede falsificar sesiones. La app no se niega a arrancar en producción | `core/config.py:16`, `docker-compose.yml:8` |
| S13 | 🟠 | Los conectores de integraciones son un objeto global compartido por todos los usuarios: lo que uno "conecta" lo usa cualquiera | `integrations/api.py:30` |
| S14 | 🟡 | Sin límite de intentos de login ni de peticiones; contraseña mínima de 6 caracteres; mensajes sin tamaño máximo (se puede saturar el LLM) | `core/auth.py`, `schemas/schemas.py:13` |
| S15 | 🟡 | Token JWT en `localStorage` (expuesto a XSS), sin revocación | `frontend/src/lib/api.js` |
| S16 | 🟡 | TEF no aplica permisos, `requires_confirmation` ni `timeout_seconds`; la auditoría vive en memoria y crece sin límite | `tef/executor.py:36`, `tef/executor.py:77` |
| S17 | 🟡 | 5 vulnerabilidades npm (2 altas) | `frontend/package-lock.json` |
| S18 | ⚪ | Usuario de prueba `demo1234` y contraseñas de desarrollo en el historial de Build A (ya público) | `adan-platform/scripts/seed_demo.py` |

### 5.3 Bugs funcionales

*Actualización 2026-09-24:* B1–B4 y B6–B18 quedaron corregidos en **WO-095**, cada uno con su prueba de regresión (`docs/wo/WO-095_REPORTE.md`). B5 sigue abierto y pasa a WO-107.

| # | Sev. | Hallazgo | Dónde |
|---|---|---|---|
| B1 | 🟠 | `POST /nivel1/{id}/recommendations` **siempre falla con 500**, después de gastar 5 llamadas al LLM: `_record_event` recibe los argumentos corridos | `services/gemelo_digital.py:199` |
| B2 | 🟠 | `/cognitive/think` **no persiste nada**: dice "8 eventos publicados", pero no queda ni un evento ni un mensaje en la BD, porque nadie hace `commit` | `cognitive/orchestrator.py:547,567`, `cognitive/event_bus.py:107` |
| B3 | 🟠 | Si el LLM falla o no devuelve JSON, el agente **vota PROCEED** por defecto. Con Ollama caído, el Board de 7 aprueba todo con confianza 0,3 | `nivel1/board_room.py:165`, `agents/board.py:536`, `ai/normalize.py:67` |
| B4 | 🟠 | El Board **aprueba sus propias decisiones** (`PROCEED` → `approved`) y el Gate Review completa el Nivel **sin aprobación del cliente**; ambas cosas contradicen AD-001 §12, AD-FUNC-01 y el Patrón A | `services/gemelo_digital.py:132`, `nivel1/service.py:392` |
| B5 | 🟠 | El Gate Review "determinístico" cuenta palabras clave en un diagnóstico que escribió el mismo LLM, al que se le pidió incluir esas palabras. No evalúa la evidencia del cliente (AD-CMP-05) | `nivel1/gate_review.py:163-392` |
| B6 | 🟡 | `recommendations` y `gate-review` vuelven a correr el Board Room completo: más costo y un resultado distinto al del diagnóstico. Cada ejecución crea además otra Decisión | `api/v1/nivel1.py:317,366` |
| B7 | 🟡 | Solo se registra el disenso del último agente que discrepa; AD-FUNC-02 exige documentar todo el disenso | `nivel1/board_room.py:208` |
| B8 | 🟡 | El chat reenvía el historial completo en cada turno y el resumen nunca se genera; en conversaciones largas se desborda el contexto del modelo | `nivel1/service.py:108-119` |
| B9 | 🟡 | En chat-stream, un token con salto de línea rompe el formato SSE, y si el cliente se desconecta la respuesta no se guarda | `api/v1/nivel1.py:189` |
| B10 | 🟡 | `MemoryService` está roto (`join()` sin destino) y nunca se usa | `services/memory.py:24` |
| B11 | 🟡 | Cada router crea su propio índice vectorial en memoria: se pierde al reiniciar y el CEO o el Board no ven lo que se ingestó por `/ems` salvo por búsqueda `LIKE` | `agents/api.py:61`, `agents/board_api.py:76`, `ems/api.py:91`, `dka/api.py:41` |
| B12 | 🟡 | El CEO "llena vacíos de información" con llamadas falsas: `COUNT(*)` de todas las empresas, `httpbin.org/get` y la calculadora con `"0"` | `agents/ceo.py:309-330` |
| B13 | 🟡 | DKA sin URLs ingiere páginas de `httpbin.org` como "conocimiento" de la empresa | `dka/pipeline.py:139-165` |
| B14 | 🟡 | Escalas de confianza inconsistentes: 0–100 en Nivel 1 y 0–1 en el Board de 7; una respuesta de "85" se muestra como 8500 % | `agents/board.py:478,521` |
| B15 | ⚪ | Completar el Nivel 7 crea un "Nivel 8" | `services/gemelo_digital.py:78` |
| B16 | ⚪ | `record_correction` hace `commit` antes de ajustar la confianza y ese ajuste nunca se guarda; `delete_document` borra físicamente, en contra de "nada se elimina" | `ems/memory.py:233-247`, `ems/memory.py:147` |
| B17 | ⚪ | Si el LLM devuelve una lista JSON, el Board lanza `AttributeError` (500) en lugar de usar el fallback | `nivel1/board_room.py:159` |
| B18 | ⚪ | `core/database.py` crea directorios a partir de `DATABASE_URL` aunque sea PostgreSQL | `core/database.py:12-13` |

### 5.4 Capacidades simuladas o desconectadas

Se presentan como funcionalidad pero no hacen el trabajo real:

- **Voz** (`voice/adapter.py`): responde "[Audio transcrito por Claro]" sin procesar audio.
- **Omnicanal** (`omnichannel/channels.py`): `respond()` devuelve `True` sin enviar nada.
- **Conectores** Gmail, Outlook, Calendar y Slack (`integrations/connectors.py`): "se conectan" sin credenciales y devuelven datos simulados.
- **Correo** (`tef/tools.py`, `email_sender`): simulado; esto sí lo declara en su respuesta.
- **Learning, Quality, Plugins, AgentFactory, Autonomous**: clases en memoria que solo usan las pruebas (`test_wo011_to_wo020.py`); ningún endpoint las expone.
- **Tool manager del orquestador cognitivo**: el paso "tool_manager" no hace nada (`cognitive/orchestrator.py:197`).

### 5.5 Arquitectura y deuda técnica

1. **Dos Board Rooms, dos orquestadores y dos mecanismos de agentes** (clases y prompts) conviven sin una decisión que los reconcilie. Ninguno implementa los 7 roles de AD-FUNC-02 (el de 7 usa CHRO en lugar de Producto).
2. **Tres bases declarativas** (`Base`, `EMSBase`, `OOSBase`) y `create_all` sin migraciones. `conftest.py` ni siquiera crea las tablas de OOS.
3. **Modelo de datos incompleto:** 11 de las 38 entidades de AD-006 v1.2. OOS modela otra organización (Departamentos, Roles, KPIs) paralela a AD-005, sin reconciliar.
4. **IA:** un solo proveedor y un modelo de 0,5B para todo, cuando el blueprint pide Haiku/Sonnet/Opus por tipo de tarea. Sin reintentos, degradación controlada ni medición de costo por proyecto (AD-IA-03).
5. **Documentación fragmentada entre builds:** la versión más completa del blueprint está en Build A, y `ADAN_MASTER_ARCHITECTURE_v1.0.md` todavía se presenta como "Single Source of Truth" aunque el Canon ya revocó ese estatus.
6. **Dependencias:** `pytest` y compañía no están en `requirements.txt`; `passlib` está sin mantenimiento y con `bcrypt` 4.2 emite advertencias.
7. **Numeración:** Build C usa WO-011 → 020 internamente (Voice, Omnichannel…), lo que choca con Build B. La conciliación sigue pendiente en `AD-ROOT-0001 §4`.

### 5.6 Operación

- El backend corre con `uvicorn --reload` y el frontend con el servidor de desarrollo de Vite dentro de Docker (`backend/start.sh:8`, `frontend/Dockerfile`).
- `npm install` sin lockfile en la imagen, y `ollama/ollama:latest` sin fijar versión.
- Sin CI/CD, sin healthchecks del backend o frontend, sin backups de la BD y sin métricas ni trazas.
- `.claude/launch.json` apunta a rutas de Build B en la laptop.

---

## 6. Qué se puede reutilizar de Build A (y de Build B cuando se importe)

| Pieza en `adan-platform/` | Sirve para |
|---|---|
| `backend/migrations/versions/f8d91060004d_*.py`: esquema Alembic de 37 tablas (26 de negocio y 11 operativas) sobre PostgreSQL | WO-091 y WO-098: es casi el modelo completo de AD-006 |
| `infra/docker-compose.yml`, `Makefile`: Postgres + pgvector + Redis con puertos ya resueltos | WO-091 y WO-093 |
| `ai/memory/*`, `backend/app/routers/kg.py`: memoria semántica y consulta híbrida grafo + semántica | WO-099 (memoria) y EMS |
| `ai/orchestrator/*`: cola y ejecutor de agentes sobre Redis | WO-099 |
| `frontend/`: React + TypeScript + Playwright E2E + ESLint, con explorador del Knowledge Graph | WO-092 |
| `contracts/openapi/schema.json` | WO-093 (contratos y pruebas de API) |
| `docs/blueprint/*`: blueprint consolidado v1.0 y AD-FUNC-07/08/09 | WO-096 (unificación documental) |

Build B (WO-000 → WO-012, tag `v1.0.0`) cubre además Gemelo Digital v1, Board Room con estrategias, Scoring, Experience, Gamification, Onboarding y Learning v1: es la mejor fuente para WO-098 → WO-118 cuando esté en el repositorio.

---

## 7. Riesgos no técnicos observados

- **El repositorio es público** y contiene documentos de negocio y de estrategia: `ADAN.docx` y `Chat 1.docx` son transcripciones de conversaciones. Conviene revisar si todo eso debe ser público.
- *Actualización 2026-09-24 (`AD-DEC-0002`):* Hernán confirma que **no hay disputa de propiedad intelectual**, así que se retira ese riesgo. La red de comisiones se mantiene como multinivel tipo Amway, con las condiciones de la Ley 1700 de 2013, que se diseñan en WO-100 y WO-121.

---

## 8. Recomendación

1. Aprobar y fusionar **WO-094** (este PR) antes de exponer cualquier instancia de ADÁN a una red.
2. Cerrar **WO-090** (tag de baseline y revisión humana, EPWO-053) y ejecutar **WO-095** (bugs B1–B18; ✅ fusionada) y **WO-096** (importar Build B y unificar la documentación) antes de construir funcionalidad nueva.
3. Seguir el plan `docs/auditoria/PLAN_WO_ADAN_100.md`: primero la plataforma (PostgreSQL, seguridad por empresa, TypeScript, producción), después el núcleo (Gemelo, Board Room único, memoria, scoring) y por último los Niveles 2–7.
