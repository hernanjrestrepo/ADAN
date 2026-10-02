# WO-093 — Producción Enterprise: CI/CD, observabilidad, seguridad · Reporte de cierre

**Formato:** EPWO-050 · **Checklist:** EPWO-051 · **Fecha:** 2026-10-02
**Estado:** ✅ **CERRADA**. El código queda listo para producción; la línea queda en estado **Piloto** hasta el primer despliegue real (`AD-DEC-0002 §D3`).
**Commits:** `25eb5e7` (seguridad y observabilidad), `8e483a7` (despliegue y CI/CD)
**Decisiones:** `AD-DEC-0002 §D4, §D8`

---

## 1. Seguridad

### Vulnerabilidades corregidas (todas con un test que falla contra el código anterior)

| # | Hallazgo | Severidad | Corrección |
|---|---|---|---|
| S1 | **OOS sin aislamiento entre clientes:** cualquier usuario autenticado podía leer y modificar work orders, KPIs, riesgos y reuniones de otra empresa conociendo su ID (13 endpoints) | Crítica | `app/core/access.py`; un recurso ajeno responde 404 |
| S2 | **Integraciones compartidas entre usuarios:** las conexiones (con credenciales de Gmail, Slack, etc.) vivían en un singleton global, así que cualquier usuario podía ejecutar acciones con la conexión de otro | Crítica | Un `ConnectorManager` por usuario |
| S3 | `python_sandbox` ejecutaba código arbitrario con los permisos del backend | Crítica | Desactivado por defecto (WO-090) |
| S4 | `file_reader` leía cualquier archivo del servidor | Alta | Confinado a `TEF_FILES_DIR` (WO-090) |
| S5 | Calculadora con `eval` escapable | Alta | Evaluador AST (WO-090) |
| S6 | SSRF en TEF, DKA e integraciones, incluso vía redirecciones (acceso a Ollama interno y a metadatos cloud) | Alta | `app/core/net.py`; se valida cada request y cada redirección |
| S7 | Dependencias con CVEs: starlette, python-multipart, python-jose, ecdsa, vite/esbuild, react-router, nanoid | Alta | Actualizadas o reemplazadas: `pip-audit` y `npm audit` sin vulnerabilidades |
| S8 | Secreto JWT por defecto aceptado en cualquier entorno | Alta | `ENVIRONMENT=production` no arranca con secretos inseguros, SQLite o CORS `*` |
| S9 | Sin límite de intentos de login | Media | Rate limit por IP; latencia constante para no revelar qué emails existen |
| S10 | Los usuarios archivados podían seguir entrando | Media | Bloqueados en login y en el uso de tokens |
| S11 | Errores 500 con detalles internos; violaciones de FK como 500 | Media | 500 genérico con `request_id`; 409 para errores de integridad |

Además: cabeceras de seguridad (CSP, `nosniff`, `X-Frame-Options: DENY`, HSTS en producción), `/docs` desactivado en producción, contenedores sin root y sin paquetes del sistema.

## 2. Observabilidad

- **`X-Request-ID`** en cada respuesta (nginx lo genera) y en **cada línea de log JSON** emitida durante la request.
- **`/metrics`** en formato Prometheus (`adan_http_requests_total`, `adan_http_request_duration_seconds`), etiquetado por plantilla de ruta y no por URL concreta, para que los IDs no disparen la cardinalidad. No se expone públicamente: nginx devuelve 404.
- **`/health`** (liveness) y **`/health/ready`** (readiness: base de datos accesible y esquema en la última migración; si no, responde 503).

## 3. CI/CD (`.github/workflows/ci.yml`)

| Job | Qué verifica |
|---|---|
| Backend | Ruff, tests en SQLite con cobertura ≥ 80%, `alembic check` |
| Backend PostgreSQL | Suite completa contra `pgvector/pgvector:pg16`, `alembic check` |
| Frontend | `npm ci`, typecheck, tests, build |
| Seguridad | `pip-audit`, `npm audit --audit-level=high` |
| Docker | Build de las imágenes de producción y validación de los dos compose |

Dependabot está configurado para pip, npm, GitHub Actions y Docker.

## 4. Despliegue de producción (`docker-compose.prod.yml`)

nginx (SPA + proxy de la API, SSE sin buffer) → backend (varios workers, migraciones serializadas) → PostgreSQL + pgvector y Ollama en la red interna. Solo se publica el puerto HTTP de nginx. El stack no arranca si faltan `POSTGRES_PASSWORD`, `JWT_SECRET` o `CORS_ORIGINS`.

## 5. Evidencias (ejecución real)

| Evidencia | Resultado |
|---|---|
| Suite backend, Python 3.12 en un venv limpio (réplica del job de CI) | 259 + 1 skip (SQLite), 260/260 (PostgreSQL), cobertura 82,6%, sin advertencias |
| Ruff | Sin hallazgos (se corrigieron 192 preexistentes) |
| `pip-audit` / `npm audit` | Sin vulnerabilidades conocidas |
| Imágenes Docker de producción | Construidas: backend 419 MB, web 93 MB |
| Stack de producción levantado | PostgreSQL, backend (`healthy`, usuario `uid 10001`), nginx; `/health/ready` = ready |
| Flujo vía nginx | Registro → empresa → chat con el LLM → Board Room (4 votos) → ingesta EMS en pgvector |
| UI en Chromium vía nginx | Board Room con consenso, sin errores de consola |
| Logs | JSON con `request_id` propagado desde nginx |

**Limitación de la verificación:** para no descargar la imagen y los modelos de Ollama (varios GB), Ollama se sustituyó por un *stub* HTTP que responde como su API. El resto del stack es exactamente el de `docker-compose.prod.yml`. Las builds usaron imágenes base con la CA del proxy de este entorno, solo localmente; los Dockerfiles del repositorio no se modificaron para eso.

## 6. Deuda técnica

- **D-1** El rate limit y las conexiones de integraciones viven en la memoria de cada proceso: con N workers, el límite efectivo es N veces el configurado y cada worker tiene sus propias conexiones. Para escalar horizontalmente, moverlos a Redis o a la base de datos.
- **D-2** No hay TLS dentro del compose: se espera un balanceador o proxy con TLS delante. HSTS ya se envía en producción.
- **D-3** No hay backups automáticos de PostgreSQL. El `README.md` incluye el comando `pg_dump` y se recomienda programarlo.
- **D-4** Los secretos van por variables de entorno (`.env`), sin gestor de secretos.
- **D-5** No hay dashboards ni alertas sobre `/metrics`: falta conectar Prometheus y Grafana.

## 7. Riesgos abiertos

- El CI de GitHub corre al subir esta rama. Si algún job fallara por diferencias de entorno, se corrige en la misma rama.
- Ollama real (modelos `qwen2.5:0.5b` y, si se usa, `nomic-embed-text`) no se ejecutó dentro del stack en esta verificación (ver §5).

## 8. Checklist EPWO-051

- [x] Evidencia objetiva · [x] Funcionalidad implementada · [x] Pruebas aprobadas · [x] Documentación actualizada
- [x] Commits realizados · [x] Baseline reproducible (CI + Docker) · [x] Validación de seguridad (EPWO-047) · [x] Deuda y riesgos registrados
