# Gate de Producción de la plataforma (hito H2)

**Preparado:** 2026-09-24, por Claude Code, al cerrar WO-093 · **Firma:** Hernán (CTO ADÁN): *pendiente*
**Referencia:** EPWO-054 (Gate de Producción). El texto de EPWO vive fuera de este repositorio. Esta lista reúne los criterios que el plan (`docs/auditoria/PLAN_WO_ADAN_100.md`) exige a la plataforma y la evidencia de cada uno.

> **Qué certifica este Gate:** que la **plataforma** (H2: WO-091, WO-097, WO-092 y WO-093) se puede operar en producción. **No** certifica el producto: los Niveles 2 a 7, el scoring por evidencia y el modelo de IA de calidad son H3 y H4. El Gate de Producción del producto completo es WO-122.

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| 1 | Base de datos de producción con migraciones versionadas | ✅ | PostgreSQL 16 + pgvector y Alembic `0001`–`0002`. En CI: `alembic check`, bajar y volver a subir (WO-091, WO-097) |
| 2 | Aislamiento entre empresas | ✅ | Autorización centralizada (`app/core/authz.py`). Pruebas de rutas ajenas con 404 (`test_wo097.py`, `test_security.py`) |
| 3 | Sin secretos por defecto; arranque seguro | ✅ | `production_problems()`: la app no arranca en producción con secretos débiles (`test_wo097.py`, `test_wo093.py`) |
| 4 | Sesión segura | ✅ | Cookie httpOnly, Secure y SameSite. Anti-CSRF, revocación y bloqueo de login (WO-097) |
| 5 | Límites de uso compartidos entre réplicas | ✅ | Redis con script Lua atómico, probado con dos instancias (`test_wo093.py`) |
| 6 | Dependencias sin vulnerabilidades conocidas | ✅ | `pip-audit` y `npm audit --audit-level=high` en CI |
| 7 | Imágenes de producción sin root, con healthcheck | ✅ | `backend/Dockerfile`, `frontend/Dockerfile` y `sandbox/Dockerfile`, etapa `production` |
| 8 | Red mínima: solo se publica nginx | ✅ | `docker-compose.prod.yml`: redes `data` y `sandbox` internas |
| 9 | Ejecución de código aislada | ✅ | Sandbox sin red ni secretos, con límites. Su aislamiento de red se prueba en CI (`smoke_prod.py --sandbox-offline`) |
| 10 | Liveness y readiness | ✅ | `/health` y `/health/ready` (base, migraciones, Redis y LLM) |
| 11 | Logs estructurados con correlación | ✅ | JSON con `request_id`, propagado desde nginx hasta el backend |
| 12 | Métricas | ✅ | `/metrics` Prometheus: peticiones, latencias, LLM y límites. Suma los workers y exige token |
| 13 | Backups verificados y restauración probada | ✅ | `backup.sh` y `restore.sh`. Restauración completa probada en local (36 tablas idénticas) y en cada corrida de CI |
| 14 | Despliegue y rollback documentados y ejercitados | ✅ | `deploy.sh` y `rollback.sh` en CI (job *production*); `docs/operacion/RUNBOOK.md` |
| 15 | CI obligatoria en cada cambio | ✅ | `.github/workflows/ci.yml` en cada push y PR a `main` |
| 16 | TLS delante del stack | ⏳ | **Depende de dónde se despliegue:** falta elegir el proveedor y poner el terminador TLS (RUNBOOK §1) |
| 17 | Monitoreo y alertas | ⏳ | Las métricas existen. Falta el Prometheus o Grafana que las recoja, y las alertas, según la infraestructura elegida |
| 18 | Backups fuera del servidor | ⏳ | El script existe. Falta el destino externo y la programación diaria, según la infraestructura elegida |
| 19 | Protección de la rama `main` | ⏳ | Configuración de GitHub que solo puede hacer el dueño: exigir el CI en verde antes de fusionar |

Los criterios **16 a 19** dependen de decisiones de infraestructura que toma Hernán: proveedor, dominio y almacenamiento. No son código. Con ellos resueltos, la plataforma queda lista para su primer piloto real (WO-108).

**Firma:** ______________________ (Hernán) · Fecha: __________
