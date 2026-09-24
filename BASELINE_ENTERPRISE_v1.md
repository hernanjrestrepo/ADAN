# BASELINE_ENTERPRISE_v1 — ADÁN Build C (WO-090, Sprint 4)

**Fecha:** 2026-07-31 · **Método:** ejecución real contra el código de `repos-active/adan` tal como está en disco (rama `feature/voice-quality`, sin comitear todavía). Ningún resultado de este documento es simulado — donde algo no se pudo verificar realmente, se dice explícitamente en vez de asumir éxito.
**Entorno de ejecución:** Python 3.11.9 (el sistema no tiene Python 3.12, que es lo que especifica `ADR-001-Vertical-Nivel-1.md` — discrepancia real, ver Limitaciones). Node/npm del sistema. Docker 29.1.2. Ollama nativo 0.30.10 corriendo en el host.

---

## 1. Backend — tests

```
203 passed, 5 failed in 39.93s   (208 tests recolectados por pytest)
```

**Los 5 fallos**, todos en `tests/test_board_room.py`:
- `test_board_room_runs_all_four_agents`
- `test_board_room_has_consensus`
- `test_board_room_votes_have_required_fields`
- `test_board_room_concurrent_execution`
- `test_consensus_majority_rule`

**Causa raíz común (verificada en el traceback, no supuesta):** `RuntimeError: There is no current event loop in thread 'MainThread'`, lanzado por `asyncio.get_event_loop()` bajo `WindowsProactorEventLoopPolicy`. Es consistente con un cambio de comportamiento de `asyncio` en versiones recientes de Python (deja de crear un loop automáticamente en el hilo principal) combinado con Windows — no se verificó si el mismo test falla igual en Linux/Python 3.12, que es el entorno para el que el proyecto fue diseñado. No se afirma que sea "solo un problema de entorno" sin más evidencia — se deja registrado como lo que se observó, con su traceback completo disponible en el log de esta sesión.

**Nota sobre el conteo:** el catálogo de Sprint 3 (grep estático) contó 214 funciones `test_`; pytest recolectó 208. La diferencia es esperable (grep cuenta líneas con el patrón, no distingue funciones auxiliares de tests reales) y no representa una pérdida de cobertura.

## 2. Backend — cobertura real (pytest-cov)

**Total: 79%** (5.359 líneas de código, 1.128 sin cubrir).

Módulos con cobertura baja, citados literalmente (no interpretados):

| Módulo | Cobertura |
|---|---|
| `app/dka/tools.py` | **0%** |
| `app/services/memory.py` | **0%** |
| `app/nivel1/service.py` | **19%** |
| `app/oos/api.py` | 51% |
| `app/nivel1/board_room.py` | 52% |
| `app/tef/tools.py` | 55% |
| `app/voice/tools.py` | 53% |

Módulos con cobertura alta (ejemplos): `app/models/models.py` 100%, `app/ems/models.py` 100%, `app/schemas/schemas.py` 100%, `app/ems/chunking.py` 100%.

## 3. Frontend — build

```
✓ 201 modules transformed, built in 4.31s
dist/assets/index-*.js   303.01 kB │ gzip: 94.78 kB
```
Build limpio, sin errores. `npm install` reportó **4 vulnerabilidades (3 moderadas, 1 alta)** vía `npm audit` — no corregidas en este Sprint (corregirlas sería alcance de otra WO, no de una congelación).

## 4. Backend — flujo real end-to-end (sin Docker, backend levantado directo con uvicorn en puerto de prueba 8059, detenido al terminar)

- `GET /health` → `{"status":"ok","app":"ADÁN","version":"0.1.0"}` (200)
- `POST /api/v1/auth/register` con dominio `.local` → **rechazado correctamente** por `email-validator` (422, "reserved name") — el mismo patrón de bug que la memoria de Build A documentó en su momento (ahí era un problema porque los datos demo usaban `.local`; acá se verifica que la validación en sí funciona).
- `POST /api/v1/auth/register` con dominio real de prueba (`wo090-verify@example.com`) → **201**, JWT emitido.
- `POST /api/v1/auth/login` con las mismas credenciales → **200**, JWT emitido.

**Efecto secundario a limpiar:** este flujo creó un usuario real (`wo090-verify@example.com`) en `backend/data/adan.db`. Queda registrado aquí para que no se confunda con un dato legítimo cuando se congele la rama en Sprint 1.

## 5. Ollama

`GET /api/tags` (puerto 11434, instancia nativa del host, no la de Docker) confirma **`qwen2.5:0.5b` presente y disponible** (el modelo que `DEFAULT_MODEL` espera), además de `nomic-embed-text` (no referenciado en el `.env.example` de Build C, posiblemente usado por otro proyecto en la misma máquina).

## 6. Docker

`docker compose -f docker-compose.yml config` → **sintaxis válida**, sin errores.

**No se levantó el stack completo de Docker en este Sprint.** El `docker-compose.yml` de Build C define su propio servicio `ollama` en el puerto `11434` — el mismo puerto donde ya corre la instancia nativa de Ollama del host (verificada en la sección 5, en uso por este mismo entorno de trabajo). Levantar el stack completo habría requerido detener esa instancia nativa o remapear el puerto, ninguna de las dos cosas se hizo unilateralmente para no interrumpir otro trabajo activo en la máquina. Esto es una limitación real de este Sprint, no un resultado simulado de éxito.

---

## 7. Limitaciones y deuda técnica (consolidado, con evidencia)

1. **Python 3.11 usado en vez de 3.12** (especificado por `ADR-001-Vertical-Nivel-1.md`). Todo lo demás funcionó sobre 3.11; no se probó sobre 3.12 real.
2. **`pytest`, `pytest-asyncio`, `pytest-cov` y `aiohttp` no están declarados en `backend/requirements.txt`** — hubo que instalarlos manualmente para poder correr la suite. `requirements.txt` solo, por sí solo, no permite ejecutar los tests.
3. **5 tests fallando** en `test_board_room.py`, causa raíz común de `asyncio` (sección 1) — sin confirmar si es un problema real de lógica o solo de entorno/SO.
4. **Tres bases declarativas SQLAlchemy separadas** (`Base`, `EMSBase`, `OOSBase`) — ya señalado en `INVENTARIO_TECNICO_ADAN.md`, relevante directamente para WO-091 (migración a Postgres).
5. **Cobertura real 0% en `dka/tools.py` y `services/memory.py`** — código presente, sin ninguna prueba que lo ejerza.
6. **Stack de Docker no verificado de punta a punta** por conflicto de puerto con Ollama nativo — ver sección 6.
7. **4 vulnerabilidades npm sin corregir** en el frontend (`npm audit`).
8. **Usuario de prueba `wo090-verify@example.com`** quedó creado en la base real durante la verificación de esta sección — pendiente de decisión (conservar como parte de la evidencia de baseline, o eliminarlo antes de congelar).
9. **Superficie de seguridad de `PythonSandboxTool`/`SqlQueryTool`** (TEF) no evaluada — señalada en el inventario técnico, no en este Sprint de baseline.
