# WO-097 — Seguridad y aislamiento por empresa

**Fecha:** 2026-09-24 · **Ejecutor:** Claude Code · **Autoriza:** Hernán ("haz todo lo que tengas que hacer", 2026-09-24)
**Formato:** EPWO-050 · **Checklist:** EPWO-051
**Estado:** ✅ Cerrada al fusionar su PR en `main`. Dos puntos pasan a otras WO (§2).

---

## 1. Fase -1

| Verificación | Resultado |
|---|---|
| Canon | `main` en `59b1c01` (WO-091 fusionada). WO-097 está en el rango asignado. |
| Alcance | La ficha de WO-097 en `PLAN_WO_ADAN_100.md` más los hallazgos pendientes S12–S18 de la auditoría. |
| Reutilización | Se reutilizó lo que ya existía: `ensure_public_url` (WO-094), `ToolMetadata.permissions`, `requires_confirmation` y `timeout_seconds` (estaban declarados pero no se aplicaban) y `cryptography`, que ya venía con python-jose. Build A no tenía nada mejor (`WO-096_MAPA_REUTILIZACION.md`: su JWT es equivalente y sus endpoints del grafo no verifican al dueño). |
| Inventario | 25 chequeos de dueño copiados en 9 routers. Conectores en un objeto global. Auditoría de TEF en una lista en memoria. Token en `localStorage`. Secreto JWT público por defecto. Sin límites de ningún tipo. |

## 2. Cambios de alcance

| Punto de la ficha | Destino | Motivo |
|---|---|---|
| Sandbox aislado para reactivar `python_sandbox` y `file_reader` | **WO-093** | Necesita infraestructura: un contenedor efímero sin red ni secretos. Mientras tanto las herramientas siguen apagadas, y ahora además exigen permisos (`read:files`, `read:database`) que nadie tiene concedidos. |
| S17: dependencias npm que exigen versiones mayores (vite 8, react-router 7) | **WO-092** | Cambian la cadena de build. Se hacen junto con la migración a TypeScript. |

## 3. Qué se hizo

| Hallazgo | Corrección |
|---|---|
| **S12:** secreto JWT público por defecto | Ya no existe ningún secreto por defecto. Sin `JWT_SECRET`, en desarrollo se genera uno al azar en cada arranque. Con `ADAN_ENV=production` la app **no arranca** si falta `JWT_SECRET` (32 caracteres o más) o `ENCRYPTION_KEY`, si la base es SQLite, si la clave de PostgreSQL es la de desarrollo o si CORS es `*`. `docker-compose.yml` ya no trae un secreto fijo. |
| **S13:** conectores globales | Cada empresa tiene sus conexiones (`integration_connections`), con las credenciales **cifradas con Fernet**. Nunca se devuelven. Cada petición crea su propio conector con las credenciales de *su* empresa. Desconectar borra las credenciales. |
| **S14:** sin límites | Contraseñas: mínimo 10 caracteres, máximo 72 bytes (límite de bcrypt), no repetitivas y distintas del correo. Login: 5 fallos por IP y correo en 15 min → 429 con `Retry-After`; el bloqueo no afecta a otras cuentas. Registro: 20 por IP y hora. Peticiones: 600 por IP y minuto. Endpoints con LLM: 30 por usuario y minuto. Cuerpo: 1 MB como máximo (413). Mensajes: 8.000 caracteres; documentos del EMS: 500.000. Todo es configurable por variable de entorno. |
| **S15:** token en `localStorage`, sin revocación | Sesión en una cookie **httpOnly, SameSite=Lax y Secure en producción**. El frontend ya no toca el token. Las peticiones con cookie que modifican datos exigen `X-Requested-With: adan` (anti-CSRF). `POST /auth/logout` incrementa `users.token_version` y revoca todos los tokens emitidos antes. La API sigue aceptando `Authorization: Bearer`. |
| **S16:** TEF sin permisos, confirmación ni timeout; auditoría en memoria | Los permisos de cada herramienta se verifican contra los concedidos (por defecto `read:web` y `write:communication`). Las herramientas con `requires_confirmation`, como enviar email, devuelven `confirmation_required` y una vista previa hasta recibir `confirm: true`. `timeout_seconds` se aplica con `asyncio.wait_for`. Cada intento queda en la tabla `tef_audit_log`; sin base, en memoria con un tope de 1.000. |
| **Autorización centralizada** | Nuevo módulo `app/core/authz.py`: `owned_companies`, `get_owned_company`, `get_owned_project`, `get_owned_organization` y `get_owned_work_order`. Reemplaza los 25 chequeos copiados. Un recurso ajeno responde siempre 404. Se revisaron **todos** los endpoints: los únicos sin autenticación son los de salud y el catálogo de herramientas, que no exponen datos. |
| **Salida controlada** | `OUTBOUND_ALLOWED_HOSTS` limita a qué hosts (y subdominios) llaman herramientas y conectores, además de la protección SSRF. httpx respeta `HTTPS_PROXY` para usar un proxy de salida. |
| **S18:** usuario `demo1234` en el historial de Build A | **Aceptado.** Es un script de datos de prueba de Build A, que nunca se desplegó y es archivo histórico. Esa contraseña no existe en Build C, y la nueva política la rechazaría. |
| Cabeceras | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` y `Referrer-Policy: same-origin`. |
| **S17 (parcial)** | `npm audit fix`, sin saltos de versión mayor: nanoid 3.3.19 (cierra la vulnerabilidad **alta**) y react-router 6.30.6. |

### Hallazgos durante la ejecución

1. **La prueba de estrés nunca probó el Board Room.** Enviaba `"Bearer $token"` literal y no verificaba el código de respuesta: todas las peticiones daban 401 en 0 s. Corregida: ahora crea la conversación, corre 5 Board Rooms a la vez y exige 200.
2. **B20 (nuevo):** con la prueba corregida, 3 de los 5 Board Rooms concurrentes fallaban con **500** cuando Ollama superaba su timeout (`httpx.ReadTimeout`). Ahora el agente que no responde **se abstiene** (la misma regla de WO-095) y el Board decide con quórum o responde "Sin consenso". Tiene prueba de regresión.
3. **Aislamiento de pruebas:** dos pruebas de aceptación escribían en la base real del backend (`backend/data/adan.db`). Ahora usan la base aislada de las pruebas.
4. **Adopción de bases antiguas (WO-091):** creaba las tablas faltantes con los modelos *actuales* y luego las marcaba `0001`, así que la migración `0002` habría fallado. Ahora completa exactamente el esquema de `0001`, reflejado de una base temporal, y deja que las migraciones siguientes hagan el resto. Tiene prueba.

## 4. Evidencia

| Evidencia | Resultado | Método |
|---|---|---|
| Suite con SQLite | **299 passed**, 5 omitidas (requieren PostgreSQL) | `pytest` |
| Suite con PostgreSQL 16 + pgvector | **303 passed**, 1 omitida | `TEST_DATABASE_URL=… pytest` |
| Pruebas de WO-097 | 31: configuración, contraseñas, bloqueo de login, límites, 413 y 422, cookie, CSRF, revocación, 7 rutas ajenas que dan 404, credenciales cifradas y aisladas, TEF (permisos, timeout, confirmación, auditoría persistente), lista de hosts de salida y B20 | `tests/test_wo097.py` |
| Migración `0002` | `upgrade`, `downgrade` y `upgrade` otra vez en SQLite y PostgreSQL; `alembic check` sin diferencias | Alembic |
| Stress real | 2 passed. 5 Board Rooms concurrentes, todos 200. Promedio 108 s, máximo 121,5 s (`qwen2.5:0.5b` en CPU). 0 errores en el log. | `tests/test_stress.py` contra un servidor en `:8050` sobre PostgreSQL + Ollama |
| Interfaz | La cookie es httpOnly y SameSite=Lax. `localStorage` está vacío y `document.cookie` no ve la sesión. POST con la cabecera: 201; sin ella: 403. La sesión sobrevive a una recarga. Tras cerrar sesión, `/auth/me` da 401. Volver a entrar funciona. El formulario exige 10 caracteres. | Playwright + Chromium contra `vite` en `:5199` |
| Frontend | Build sin errores. `npm audit`: de 5 vulnerabilidades (2 altas) a 4 (1 alta, del servidor de desarrollo vite/esbuild) | `vite build`, `npm audit` |
| Docker Compose | Válido | `docker compose config` |

## 5. Deuda y riesgos

- **Límites en memoria:** valen por proceso. Con varias réplicas hay que pasarlos a Redis (WO-093).
- **El límite de tamaño usa `Content-Length`:** una petición `chunked` sin esa cabecera no lo pasa por el middleware. Los modelos de Pydantic siguen limitando los campos de texto.
- **Cerrar sesión cierra todas las sesiones** del usuario: es el costo de revocar sin guardar estado por sesión. Una lista de sesiones por dispositivo queda para cuando se necesite.
- **`access_token` sigue en la respuesta JSON** de login y registro, para los clientes de la API y las pruebas. El frontend no lo usa.
- **Vulnerabilidades npm restantes** (vite/esbuild, solo del servidor de desarrollo, y react-router): pasan a WO-092.
- **`qwen2.5:0.5b` en CPU:** 5 deliberaciones a la vez saturan Ollama y algunos agentes se abstienen por timeout. Se resuelve con el enrutamiento de modelos (WO-099) y la infraestructura de producción (WO-093).
- **Documentos históricos** (`docs/BASELINE_NIVEL1.md`, `docs/FROZEN_INTERFACES.md`) todavía citan el antiguo secreto por defecto. Describen el estado de su fecha; no se editan.

## 6. Checklist EPWO-051

- [x] Evidencia objetiva ejecutada (§4).
- [x] Pruebas que pasan en los dos motores.
- [x] Una prueba por cada hallazgo corregido.
- [x] Documentación (README, auditoría, plan) y deuda registradas.
- [x] Cambios de alcance registrados y trasladados (§2).
- [x] `git status` limpio al hacer el commit.
- [x] Reporte en `docs/wo/`.
- [x] PR fusionado a `main`.
