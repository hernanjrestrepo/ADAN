# REPORTE_CONSOLIDACION_WO090

**WO-090 — Consolidación Oficial de ADÁN Enterprise** (renumerada de la propuesta original "WO-100" — ver hallazgo bloqueante §3)
**Fecha:** 2026-07-31 · **Ejecutor:** esta sesión (Claude Code) · **Autoriza:** Hernán (CTO ADÁN)
**Formato:** EPWO-050 (cierre de Work Order) · **Checklist:** EPWO-051
**Estado:** 🟡 **ABIERTA.** No cumple simultáneamente el checklist de EPWO-051 — ver §7. Esto es esperado en este punto, no un error: el propio alcance de esta WO deja el commit de congelación pendiente de aprobación explícita.

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
