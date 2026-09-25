# Runbook de operación de ADÁN

**Desde:** WO-093 (2026-09-24). **Para:** quien despliega y opera ADÁN en producción.

---

## 1. Arquitectura de producción

`docker-compose.prod.yml`:

```
Internet ──TLS──► balanceador/proxy (fuera del compose; termina HTTPS)
                        │
                        ▼  HTTP_PORT → 8080
                   frontend (nginx, sin root)
                   · sirve la interfaz (SPA)
                   · proxy /api, /ems, /tef, /agents, /board, /oos, /dka,
                     /integrations, /voice, /omnichannel y /health → backend
                        │ red "web"
                        ▼
                   backend (uvicorn, N workers, sin root)
                   ├─ red "data" (interna) ──► postgres (pgvector) · redis
                   ├─ red "sandbox" (interna) ──► sandbox (sin red externa)
                   └─ red "llm" ──► ollama
```

- Solo se publica nginx. PostgreSQL, Redis y el sandbox están en redes internas, sin salida a internet.
- Las migraciones las corre el servicio `migrate` antes del backend. El backend de producción no migra al arrancar.
- **TLS es obligatorio.** La cookie de sesión es `Secure` y no viaja por HTTP. Delante del compose va un balanceador o un proxy con certificado: Caddy, Traefik, nginx con Let's Encrypt, o el balanceador del proveedor de nube.

## 2. Primera instalación

```bash
cp .env.prod.example .env.prod      # completar TODOS los secretos
chmod 600 .env.prod
ENV_FILE=.env.prod scripts/deploy.sh
# Modelos de Ollama (una sola vez; quedan en el volumen ollama-models)
docker compose -f docker-compose.prod.yml --env-file .env.prod exec ollama ollama pull qwen2.5:0.5b
docker compose -f docker-compose.prod.yml --env-file .env.prod exec ollama ollama pull nomic-embed-text
```

Con `ADAN_ENV=production`, la app **no arranca** en estos casos:
- falta `JWT_SECRET` o `ENCRYPTION_KEY`;
- la base es SQLite;
- la clave de PostgreSQL es la de desarrollo;
- CORS es `*`;
- `SANDBOX_TOKEN` es corto.

## 3. Despliegue

```bash
ENV_FILE=.env.prod scripts/deploy.sh            # etiqueta = commit actual
```

Pasos del script:
1. Construye las imágenes con la etiqueta.
2. Hace un backup (`backups/`).
3. Corre las migraciones.
4. Levanta los servicios.
5. Espera a que `/health/ready` responda "ready".

Guarda la etiqueta desplegada en `.deployed_tag`.

## 4. Rollback

```bash
# La versión anterior no cambió el esquema:
ENV_FILE=.env.prod scripts/rollback.sh <etiqueta-anterior>

# La versión nueva agregó migraciones: primero se revierten, con el código nuevo
ENV_FILE=.env.prod scripts/rollback.sh <etiqueta-anterior> <revision-de-alembic-anterior>
```

`docker compose -f docker-compose.prod.yml run --rm migrate alembic history` lista las revisiones.

Si una migración no se puede revertir, se restaura el backup previo al despliegue (§5).

## 5. Backups y restauración

```bash
ENV_FILE=.env.prod scripts/backup.sh backups                 # pg_dump -Fc + verificación + SHA-256
CONFIRM=si ENV_FILE=.env.prod scripts/restore.sh backups/adan-AAAAMMDDTHHMMSSZ.dump
```

- `backup.sh` verifica que el archivo se puede leer (`pg_restore --list`) y guarda su suma SHA-256.
- `restore.sh` exige `CONFIRM=si`, verifica la suma, detiene el backend, restaura (`--clean`) y lo vuelve a levantar.
- Programar `backup.sh` a diario con cron o un temporizador de systemd, y copiar `backups/` **fuera del servidor** (almacenamiento de objetos, otra región).
- **Probar la restauración** al menos una vez al mes en una base aparte, con `RESTORE_DATABASE_URL=...`. El CI prueba la restauración completa en cada cambio (`.github/workflows/ci.yml`, job *production*).

## 6. Salud, logs y métricas

| Qué | Dónde |
|---|---|
| Liveness | `GET /health`, público a través de nginx |
| Readiness | `GET /health/ready`, solo en la red interna: base, migraciones, Redis y LLM. 503 si la base o las migraciones fallan; el LLM caído se reporta como degradado y no saca al backend de servicio. |
| Logs | JSON por stdout (`docker compose logs backend`). Cada línea de una petición trae su `request_id`, el mismo que nginx pone en `X-Request-ID` y que recibe el cliente. |
| Métricas | `GET /metrics`, solo en la red interna, con `Authorization: Bearer $METRICS_TOKEN`: peticiones por ruta y código, latencias, llamadas al LLM y rechazos por límites. Suma todos los workers. |

Para seguir un error que reporta un usuario: pedirle el `request_id`, que aparece en la respuesta 500, y buscarlo en los logs.

## 7. Sandbox

`python_sandbox` solo existe si hay sandbox (`SANDBOX_URL`). El contenedor:
- corre con raíz de solo lectura, `/tmp` en memoria, sin capacidades, `no-new-privileges`, 128 procesos, 512 MB y 1 CPU;
- vive en una red interna sin salida;
- cada ejecución tiene además límites de CPU, memoria, archivos y tiempo, y un entorno vacío.

El código del sandbox puede llamar al backend por la red interna, como cualquier cliente del API. Por eso `/metrics` exige token.

## 8. Incidentes frecuentes

| Síntoma | Qué revisar |
|---|---|
| `/health/ready` da 503 por migraciones "pendientes" | Hubo un despliegue sin `migrate`: correr `docker compose ... run --rm migrate` |
| El login no mantiene la sesión | Se accede por HTTP: la cookie es `Secure` y exige TLS |
| Respuestas 429 | Límites de `RATE_LIMIT_PER_MINUTE`, `LLM_RATE_LIMIT_PER_MINUTE` o `LOGIN_MAX_FAILURES`; revisar `adan_rate_limited_total` en `/metrics` |
| El Board Room se abstiene siempre | El modelo local no produce JSON válido (WO-099) |
| Redis caído | Los límites dejan pasar (fail-open) y `/health/ready` reporta el error |
