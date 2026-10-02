# REPORTE_CONSOLIDACION_WO090

**WO-090 — Consolidación Oficial de ADÁN Enterprise** (renumerada de la propuesta original "WO-100" — ver hallazgo bloqueante §3)
**Fecha:** 2026-07-31 · **Ejecutor:** esta sesión (Claude Code) · **Autoriza:** Hernán (CTO ADÁN)
**Formato:** EPWO-050 (cierre de Work Order) · **Checklist:** EPWO-051
**Estado:** ✅ **CERRADA el 2026-10-01** (ver §10). *Estado original del 2026-07-31: 🟡 ABIERTA, pendiente del commit de congelación y de decisiones de Hernán, que se tomaron por delegación en `AD-DEC-0002`.*

---

## 1. Resultado consolidado

Los 4 entregables de Sprints 2-4 están completos con evidencia real (no inspección de código — EPWO-018): catálogo de Work Orders, inventario técnico, baseline de certificación con tests/build/E2E ejecutados de verdad. Sprint 1 (congelación en git) está preparado pero no ejecutado — requiere tu aprobación explícita antes de comitear (instrucción original de esta WO).

## 2. Evidencias objetivas (EPWO-017/018/021)

| Evidencia | Resultado | Método |
|---|---|---|
| Suite de tests backend | 203 passed, 5 failed (208 recolectados) | `pytest` real, 39.93s |
| Cobertura real | 79% (5.359 líneas, 1.128 sin cubrir) | `pytest-cov` real |
| Build frontend | 201 módulos, sin errores, 4.31s | `npm run build` real |
| Flujo E2E auth | register→login con JWT real, validación de dominio reservado rechazada correctamente | HTTP real contra backend levantado (puerto 8059, detenido al cerrar — EPWO-016) |
| Ollama | `qwen2.5:0.5b` confirmado disponible | `curl` real a la instancia nativa (11434) |
| Docker | `docker compose config` válido | Ejecutado; stack completo NO levantado (ver §5, riesgo documentado, no simulado) |
| Seguridad — hashing de password | `bcrypt` real vía `passlib.CryptContext`, verificado en `app/core/auth.py` | Lectura de código + confirmado que el password nunca aparece en la respuesta de login (HTTP real) |
| Seguridad — autorización | Endpoint de companies devuelve `403 Not Authenticated` ante intento sin token (incluida una carga con sintaxis de inyección SQL en la URL) | HTTP real. **No concluyente como prueba de resistencia a SQLi específicamente** — el request fue bloqueado por autenticación antes de llegar a la capa de datos; no se hizo una prueba de inyección post-autenticación en este Sprint. |

Tiempo real de ejecución (EPWO-025, wall-clock, no estimado): instalación de entorno backend ~90s, suite de tests 39.93s, `npm install` 56s, build frontend 4.31s, verificaciones HTTP manuales <1 min cada una.

## 3. Hallazgos, clasificados por EPWO-009 (Bloqueante / No bloqueante)

**Bloqueante (detuvo la ejecución, se resolvió dentro de esta WO):**
- Colisión de numeración: "WO-100" ya reservado para *Business Architecture* en el blueprint original; "WO-101-103" se superponían con la reserva de cadena SaaS de `CHAIN_CLOSURE.md`. Resuelto: renumerado a WO-090/091/092/093, registrado en `AD-ROOT-0001 §4` y motivó la Regla 7 de `AD-GOV-0001` (Fase -1).

**No bloqueantes (no se corrigieron dentro de esta WO — quedan como deuda técnica o recomendación de WO futura, por EPWO-010):**
1. 5 tests de `test_board_room.py` fallan por `RuntimeError` de `asyncio` bajo Python 3.11/Windows — no confirmado si ocurre también en el entorno objetivo (Python 3.12).
2. `pytest`, `pytest-asyncio`, `pytest-cov`, `aiohttp` no declarados en `backend/requirements.txt`.
3. Tres bases declarativas SQLAlchemy separadas (`Base`, `EMSBase`, `OOSBase`) — relevante para WO-091 (migración a Postgres).
4. Cobertura 0% en `app/dka/tools.py` y `app/services/memory.py`.
5. Stack Docker no verificado de punta a punta (conflicto de puerto 11434 con Ollama nativo en uso).
6. 4 vulnerabilidades npm (3 moderadas, 1 alta) sin corregir.
7. Prueba de resistencia a inyección SQL post-autenticación no realizada (ver §2).
8. Superficie de seguridad de `PythonSandboxTool`/`SqlQueryTool` (TEF) no evaluada.
9. Usuario de prueba real `wo090-verify@example.com` creado en la base durante verificación E2E — **etiquetado el 2026-07-31** (`name` actualizado a `WO090_VERIFICATION_USER` en `backend/data/adan.db`, por instrucción explícita de Hernán) para que sea identificable como dato de verificación y no se confunda con un usuario real. **No eliminado todavía** — decisión pendiente hasta el cierre de esta WO: se elimina o se convierte en usuario de demostración.
10. Estados EPWO-029 (Experimental/Piloto/Producción/Deprecado) aún no aplicados formalmente a Build A/B/C — `AD-DEC-0001` usa terminología propia ("archivado", "referencia técnica", "línea oficial") que debe reconciliarse con la taxonomía estándar de EPWO en una próxima revisión del Canon.

## 4. Deuda técnica (consolidado de §3, sin duplicar)

Ver lista completa en §3 "No bloqueantes" — las 10 quedan registradas ahí, no se repiten aquí por EPWO-010.

## 5. Riesgos abiertos

- **Ninguna de las tres líneas está comitada en la rama oficial todavía** — mientras eso no ocurra, el estado real de Build C solo existe en el disco de esta máquina, sin respaldo remoto (riesgo de pérdida, EPWO-027.5).
- El conflicto de puerto Docker/Ollama nativo puede repetirse en cualquier verificación futura mientras ambos convivan en la misma máquina de desarrollo.
- La brecha de numeración interna WO-013→WO-015 de Build C sigue sin explicación documental (heredada, no introducida por esta WO).

## 6. Dependencias externas

- Confirmación de nombre de rama definitivo (`adan/enterprise` es propuesta, no decisión).
- Decisión sobre el usuario de prueba `wo090-verify@example.com`.
- Aprobación explícita de Hernán para ejecutar el commit de congelación (Sprint 1), por instrucción original de esta WO.

## 7. Checklist EPWO-051 (todas deben cumplirse simultáneamente para cerrar)

- [x] Evidencia objetiva
- [x] Documentación actualizada
- [ ] ~~Funcionalidad implementada~~ — No aplica: WO-090 es de consolidación, no agrega funcionalidad (EPWO-013), por diseño.
- [ ] Pruebas aprobadas — 203/208; los 5 fallos están clasificados como no bloqueantes (§3) pero no están corregidos, así que no se marcan "aprobadas" sin reserva.
- [ ] Repositorio limpio (`git status`) — pendiente, Sprint 1 no ejecutado.
- [ ] Commits realizados (por Sprint y final) — ninguno todavía.
- [ ] Baseline reproducible desde el repositorio — no, porque nada está comiteado (EPWO-035).
- [ ] Validación de seguridad aplicable completada (EPWO-047) — parcial: hashing y exposición de password verificados; inyección SQL post-auth y superficie de TEF quedan pendientes (§3.7, §3.8).
- [x] Alcance no modificado sin registro (EPWO-008 a EPWO-010)
- [x] Deuda técnica registrada
- [x] Riesgos abiertos documentados

**Conclusión del checklist: WO-090 permanece ABIERTA**, consistente con EPWO-051 — falta más de un ítem CRITICAL/HIGH.

## 8. Recomendación de la siguiente Work Order

Una vez cerrado Sprint 1 (congelación) de WO-090 con tu aprobación, la secuencia ya acordada en `AD-ROOT-0001 §4` es:
- **WO-091 — Migración Enterprise** (PostgreSQL + pgvector), que además debería absorber la unificación de las tres bases declarativas SQLAlchemy (hallazgo §3.3) como parte de su propio alcance, no como WO adicional.
- Antes de WO-091, considerar una WO corta (o un ítem de Sprint 1) que cierre los hallazgos de seguridad no concluyentes de §3.7/§3.8 — tocan autenticación y ejecución de código, están dentro del criterio de EPWO-047, y son más baratos de cerrar ahora que después de migrar la base de datos.

---

## 9. Actualización 2026-10-01 — cierre de hallazgos técnicos (sesión Claude Code, rama `claude/amazing-allen-ta66ry`)

Verificado ejecutando, no por inspección (Linux, Python 3.11):

| Hallazgo §3 | Acción | Evidencia |
|---|---|---|
| 1. 5 fallos `test_board_room.py` | **Corregido.** No era exclusivo de Windows: `asyncio.get_event_loop()` falla sin loop activo en Python ≥3.10 en cualquier SO. Reemplazado por `asyncio.run()`. | 5/5 pasan |
| — (nuevo) `test_stress.py` enviaba `"Bearer $token"` literal (sintaxis JS) | **Corregido** a f-string. | 2/2 pasan contra backend real en :8050 |
| 2. Dependencias de test no declaradas | **Corregido:** `backend/requirements-dev.txt` (`pip install -r requirements-dev.txt`). | Suite corre con solo ese archivo |
| 4. 0% cobertura `dka/tools.py`, `services/memory.py` | Abierto. | — |
| 6. Vulnerabilidades npm | **Parcial:** `npm audit fix` aplicado (nanoid). Quedan 4 (esbuild/vite dev-server, react-router <7) que exigen subir versión mayor — requieren prueba de UI, no se forzaron. | `npm run build` OK |
| 7/8. Seguridad TEF | **Corregido.** Ver abajo. | 8 tests nuevos en `TestTEFSecurity` |

**Endurecimiento TEF (`backend/app/tef/tools.py`):**
- `calculator`: `eval` reemplazado por evaluador AST (bloquea escapes tipo `().__class__...` y exponentes gigantes).
- `python_sandbox`: no era un sandbox (ejecución remota de código para cualquier usuario autenticado). **Desactivado por defecto**; se habilita con `TEF_ENABLE_PYTHON_SANDBOX=true`. Usa intérprete aislado (`-I`) y timeout máximo 30s.
- `file_reader`: confinado a `TEF_FILES_DIR` (default `backend/data/files`); bloquea `/etc/passwd`, `../`.
- `http_request`: bloquea esquemas no http(s) y destinos loopback/privados/link-local (SSRF a Ollama, metadatos cloud). `TEF_ALLOW_PRIVATE_HTTP=true` lo desactiva. Riesgo residual: DNS rebinding.
- `sql_query`: **nunca funcionó** con SQLAlchemy 2 (faltaba `text()`) — corregido. Bloquea sentencias múltiples, `PRAGMA`/`ATTACH`/etc. y la tabla `users`/`hashed_password`.

**Resultado de la suite:** 209 passed, 7 failed de 216. Los 7 fallos son de entorno: 5 requieren acceso a `httpbin.org` (bloqueado en el contenedor de verificación) y 2 de `test_stress.py` requieren el backend levantado en :8050 (pasan cuando lo está). En la laptop con internet y backend activo se espera 216/216.

**Pendientes de decisión a esa fecha** (commit de congelación, usuario de verificación §3.9, EPWO-029 §3.10, WO-091/092/093): resueltos en §10 y `AD-DEC-0002`.

---

## 10. Cierre — 2026-10-01

Decisiones pendientes resueltas por delegación de Hernán en **`AD-DEC-0002`**:

| Pendiente (§6) | Resolución |
|---|---|
| Rama oficial / commit de congelación | Repositorio `github.com/hernanjrestrepo/ADAN`, rama `laptop`. La congelación de Build C es el commit `abc6b6c`; los cambios posteriores están en commits por WO (`AD-DEC-0002 §D1`) |
| Usuario `wo090-verify@example.com` (§3.9) | Se archiva, no se borra: `python -m scripts.archive_user wo090-verify@example.com` (`§D2`) |
| Estados EPWO-029 (§3.10) | A y B: Deprecado; C: Piloto (`§D3`) |

Hallazgos no bloqueantes de §3, estado final:

| # | Estado |
|---|---|
| 1. Tests de `test_board_room.py` | ✅ Corregidos (`c4b7826`) |
| 2. Dependencias de test no declaradas | ✅ `requirements-dev.txt` |
| 3. Tres bases declarativas | ✅ Unificadas en WO-091 |
| 4. Cobertura 0% (`dka/tools.py`, `services/memory.py`) | ✅ `dka/tools.py` al 100%; `services/memory.py` eliminado (código muerto con fuga de datos entre empresas) |
| 5. Stack Docker no verificado | ✅ Stack de producción levantado y probado (WO-093 §5) |
| 6. Vulnerabilidades npm | ✅ 0 (WO-092) |
| 7. Inyección SQL post-autenticación | ✅ Sin SQL construido con texto del usuario en la API; `sql_query` (TEF) restringida y probada; se agregó aislamiento entre clientes (WO-093 S1) |
| 8. Superficie TEF | ✅ Corregida (WO-093 S3-S6) |
| 9. Usuario de verificación | ✅ `§D2` |
| 10. EPWO-029 | ✅ `§D3` |

### Checklist EPWO-051 (final)

- [x] Evidencia objetiva
- [x] Documentación actualizada
- [x] Funcionalidad implementada: no aplica (WO de consolidación), por diseño
- [x] Pruebas aprobadas: 260/260 en PostgreSQL; 259 + 1 skip en SQLite
- [x] Repositorio limpio y commits realizados (por WO)
- [x] Baseline reproducible desde el repositorio (CI)
- [x] Validación de seguridad completada (WO-093)
- [x] Alcance no modificado sin registro (`AD-DEC-0002`)
- [x] Deuda técnica registrada · [x] Riesgos abiertos documentados

**WO-090: CERRADA.**
