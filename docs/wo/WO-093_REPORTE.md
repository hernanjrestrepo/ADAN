# WO-093 — Producción Enterprise

**Fecha:** 2026-09-24 · **Ejecutor:** Claude Code · **Autoriza:** Hernán ("haz todo lo que tengas que hacer", 2026-09-24)
**Formato:** EPWO-050 · **Checklist:** EPWO-051 · **Gate:** EPWO-054 (`docs/operacion/GATE_PRODUCCION_H2.md`)
**Estado:** ✅ Cerrada al fusionar su PR en `main`. El Gate de Producción de la plataforma queda preparado, con 15 de 19 criterios cumplidos. Los 4 restantes dependen de la infraestructura que elija Hernán, y el Gate lo firma él.

---

## 1. Fase -1

| Verificación | Resultado |
|---|---|
| Canon | WO-093 definida en `AD-ROOT-0001 §4`. `main` estaba en `8ee18f4` (WO-092). |
| Reutilización | La CI de Build A (`adan-platform/.github/workflows/ci.yml`: servicios Postgres y Redis) sirvió de base para el job *backend*. No había imágenes de producción, observabilidad ni backups en ninguna build. |
| Alcance | La ficha de WO-093, más lo que le pasaron otras WO: el sandbox aislado y los límites en Redis (de WO-097). |
| Hallazgos previos | `pip-audit` encontró **35 vulnerabilidades** en 4 paquetes (starlette, python-multipart, python-jose y ecdsa, esta última sin parche). Se resolvieron en esta WO (§2). |

## 2. Qué se hizo

| Pieza | Detalle |
|---|---|
| **Dependencias** | fastapi 0.141 con starlette 1.7 y python-multipart 0.0.32. **PyJWT** reemplaza a python-jose y deja fuera ecdsa, que no tiene parche. **bcrypt directo** reemplaza a passlib, que no tiene mantenimiento; los hashes existentes siguen validando, con prueba sobre un hash real de passlib. `pip-audit`: **0 vulnerabilidades**. |
| **GitHub Actions** | `.github/workflows/ci.yml`, en cada push y PR, con tres jobs.<br>**backend:** pip-audit; pruebas con SQLite y con PostgreSQL + pgvector (con Redis); pruebas del sandbox; migraciones (subir, verificar, bajar, subir); backup y restauración.<br>**frontend:** tipos, lint, build, `npm audit` y E2E con Chromium.<br>**production:** compose válido; `deploy.sh`; prueba de humo **con el aislamiento de red del sandbox**; backup, `rollback.sh` y restauración; prueba de humo otra vez. |
| **Imágenes** | Dockerfiles multi-etapa.<br>**backend:** `development` / `production`, sin root, con varios workers, `--proxy-headers` y healthcheck.<br>**frontend:** `development` / `production`, nginx sin root con CSP, cabeceras sin duplicar, caché de assets, SPA y proxy con timeout de 300 s para el Board y SSE sin buffer.<br>**sandbox:** sin root.<br>Hay `.dockerignore` en cada uno. |
| **docker-compose.prod.yml** | Solo nginx publicado. Redes `data` y `sandbox` **internas**. `migrate` corre antes del backend. Los secretos son obligatorios (`${VAR:?}`). El sandbox tiene raíz de solo lectura, `/tmp` en memoria, `cap_drop: ALL`, `no-new-privileges` y límites de procesos, memoria y CPU. Se incluye `.env.prod.example`. |
| **Healthchecks** | `/health` (liveness). `/health/ready` (readiness): base, migraciones al día, Redis y LLM. Si el LLM está caído se reporta como degradado, sin sacar al backend de servicio. |
| **Logs, métricas y trazas** | `X-Request-ID` de punta a punta: nginx lo genera, el backend lo pone en cada línea de log y el cliente lo recibe. Log de acceso en JSON. Un error 500 devuelve el `request_id`. `/metrics` Prometheus con la plantilla completa de la ruta (sin una serie por id), latencias, LLM (`InstrumentedLLM`) y rechazos por límites. Modo multiproceso para varios workers y protección con `METRICS_TOKEN`. `/docs` apagado en producción. |
| **Límites en Redis** | `RedisSlidingWindowLimiter`: ventana deslizante con script Lua atómico, compartida entre réplicas. Si Redis cae, deja pasar y la readiness lo reporta. |
| **Sandbox** | Servicio `sandbox/`, solo con la biblioteca estándar. Cada ejecución corre en un proceso hijo con `python -I -S`, entorno vacío, carpeta temporal propia y límites de CPU, memoria, archivos, descriptores y procesos, más timeout. Autenticación por token. Tope de concurrencia. `python_sandbox` vuelve a existir **solo** con `SANDBOX_URL`, y el permiso `execute:code` solo se concede entonces. `file_reader` y `sql_query` siguen apagadas: leen el servidor y la base sin aislamiento. |
| **Backups** | `backup.sh`: `pg_dump -Fc`, verificado con `pg_restore --list`, más SHA-256. `restore.sh`: exige `CONFIRM=si`, verifica la suma, detiene el backend y restaura. Funciona vía Docker o por conexión directa. |
| **Despliegue y rollback** | `deploy.sh`: construye, hace backup, migra, levanta y espera la readiness. `rollback.sh`: vuelve a la etiqueta anterior y, si hace falta, baja las migraciones con el código nuevo. `wait_ready.sh`. |
| **Documentación** | `docs/operacion/RUNBOOK.md` (arquitectura, instalación, despliegue, rollback, backups, observabilidad, sandbox e incidentes) y `docs/operacion/GATE_PRODUCCION_H2.md`. |

## 3. Evidencia

| Evidencia | Resultado | Método |
|---|---|---|
| Suite con SQLite | **313 passed**, 5 omitidas | `pytest`, local |
| Suite con PostgreSQL 16 + pgvector (con Redis) | **317 passed**, 1 omitida | `TEST_DATABASE_URL`, `REDIS_TEST_URL`, local |
| Sandbox | 9 passed: salida, entorno sin secretos, timeout, memoria, carpeta propia, truncado, token y validación | `sandbox/test_sandbox.py` |
| `pip-audit` | 35 → **0** vulnerabilidades | local y CI |
| Stack de producción local, sin Docker | Migración como paso aparte. Backend `ADAN_ENV=production` con 2 workers, Redis y sandbox. nginx con la configuración real. **16 verificaciones de humo** pasaron. `/docs` da 404, `/metrics` sin token da 401 y la readiness reporta todo ok. | `scripts/smoke_prod.py` |
| Correlación | El `request_id` generado por nginx aparece en el log del backend | log de acceso |
| Métricas con 2 workers | 30 peticiones → contador en 30 (suma multiproceso) | `/metrics` |
| Backup y restauración | 36 tablas con los mismos conteos, extensión `vector` y migración `0002` restauradas. Un backup alterado se rechaza. | `backup.sh` y `restore.sh` contra PostgreSQL 16 |
| Scripts de shell | Sin avisos | `shellcheck` |
| CI en GitHub | Los 3 jobs en verde (§4) | GitHub Actions |

## 4. CI en GitHub

Corrida [36075187078](https://github.com/hernanjrestrepo/ADAN/actions/runs/36075187078) sobre `45fd0ae`:

| Job | Resultado |
|---|---|
| **Backend** | `pip-audit` sin vulnerabilidades. SQLite: **313 passed**, 5 omitidas. PostgreSQL 16 + pgvector con Redis: **317 passed**, 1 omitida. Sandbox: 9 passed. Migraciones: `alembic check` sin diferencias, bajada a `base` y subida otra vez. Backup y restauración en otra base con los mismos datos y la misma revisión. |
| **Frontend** | Tipos, lint, build, `npm audit` y E2E con Chromium. |
| **Stack de producción (Docker)** | `deploy.sh` con las imágenes `production`. Prueba de humo: **18 verificaciones**, entre ellas que el sandbox no sale a internet y no ve la base de datos. Backup, `rollback.sh`, `restore.sh` y readiness (`migrations: ok (0002)`). Prueba de humo otra vez: 16 verificaciones. |

La primera corrida ([36074569327](https://github.com/hernanjrestrepo/ADAN/actions/runs/36074569327)) falló en la prueba de aislamiento del sandbox, aunque el aislamiento sí funcionaba. `python_sandbox` guardaba solo los primeros 2000 caracteres del traceback, y el nombre de la excepción (`URLError`) está al final. Se corrigió para guardar el final, y hay una prueba que lo cubre (`test_python_runs_in_the_sandbox`).

## 5. Deuda y riesgos

- **Criterios 16 a 19 del Gate** (TLS, monitoreo y alertas, backups fuera del servidor, protección de `main`): dependen de la infraestructura que elija Hernán.
- **El sandbox puede llamar al backend** por la red interna, como cualquier cliente del API. Por eso `/metrics` exige token. Si se necesita cortar también esa vía, el siguiente paso es un sandbox sin red y con cola de trabajos.
- **Rate limiting fail-open:** si Redis cae, los límites no se aplican hasta que vuelva. La readiness lo marca.
- **`starlette.testclient`** avisa que pasará a `httpx2`: se actualiza cuando starlette lo exija.
- **La imagen de Ollama** está en `latest` y el modelo por defecto sigue siendo `qwen2.5:0.5b`. La calidad del LLM se resuelve en WO-099.

## 6. Checklist EPWO-051

- [x] Evidencia objetiva ejecutada (§3, §4).
- [x] Pruebas que pasan en local y en CI.
- [x] Documentación (RUNBOOK, Gate, README, Canon y plan) y deuda registradas.
- [x] `git status` limpio al hacer el commit.
- [x] Reporte en `docs/wo/`.
- [x] PR fusionado a `main`, con el CI en verde.
