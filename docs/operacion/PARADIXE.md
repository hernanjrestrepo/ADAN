# ADAN en https://adan.paradixe.xyz

Desplegado el 2026-10-24 en el servidor Oracle de Paradixe (157.137.200.15), el mismo que corre Xmart Travel.

## Cómo está armado

| Pieza | Dónde |
|---|---|
| Código | `/srv/adan/app` (clon de `hernanjrestrepo/ADAN`) |
| Secretos | `/srv/adan/app/.env.prod` (permisos 600; generados en el servidor, nunca salen de ahí) |
| Stack | `docker-compose.prod.yml` + `docker-compose.paradixe.yml` (proyecto `adan`: backend, frontend, Postgres, Redis, Ollama, sandbox) |
| HTTPS | El Caddy de Xmart (`xmart-caddy-1`) atiende `adan.paradixe.xyz` y lo pasa a `adan-web:8080` por la red `xmart_default`. Certificado de Let's Encrypt. |
| DNS | Cloudflare, zona `paradixe.xyz`: registro A `adan` → 157.137.200.15, con proxy (nube naranja), modo SSL **Full** |
| IA | Kimi (Moonshot), `LLM_CLOUD_PROVIDER=kimi`, misma cuenta que Xmart. Ollama local con `qwen2.5:0.5b` (respaldo) y `nomic-embed-text` (memoria). |

El bloque de Caddy vive en el repositorio de Xmart (`infrastructure/produccion/Caddyfile`, variable `ADAN_DOMINIO`), para que
un despliegue de Xmart no lo borre. Si ADAN está caído, solo `adan.paradixe.xyz` responde error: Xmart no se entera.

## Actualizar

```bash
ssh -i ~/.ssh/xmart_oracle ubuntu@157.137.200.15
cd /srv/adan/app && git pull
sudo env COMPOSE_OVERRIDE=docker-compose.paradixe.yml ENV_FILE=.env.prod bash scripts/deploy.sh $(git rev-parse --short HEAD)
```

`deploy.sh` saca un backup de la base antes de migrar y verifica la salud al final. Rollback: `scripts/rollback.sh <etiqueta>`
con el mismo `COMPOSE_OVERRIDE`.

## Comprobar

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://adan.paradixe.xyz/          # 200
curl -s -o /dev/null -w "%{http_code}\n" https://adan.paradixe.xyz/api/v1/auth/me   # 401 sin sesión
```

## Pendiente

- La base de producción empieza vacía: las empresas de la laptop (Xmart Travel y sus pruebas) no se migraron.
- Backups fuera del servidor (hoy `deploy.sh` los deja en `/srv/adan/app/backups`).
