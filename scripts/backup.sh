#!/usr/bin/env bash
# Backup de PostgreSQL en formato custom, verificado y con suma SHA-256 (WO-093).
#
#   scripts/backup.sh [directorio]                    # vía docker compose (docker-compose.prod.yml)
#   BACKUP_DATABASE_URL=postgresql://... scripts/backup.sh [directorio]   # conexión directa
set -euo pipefail
OUT_DIR="${1:-backups}"
mkdir -p "$OUT_DIR"
FILE="$OUT_DIR/adan-$(date -u +%Y%m%dT%H%M%SZ).dump"
COMPOSE="docker compose -f ${COMPOSE_FILE:-docker-compose.prod.yml} ${ENV_FILE:+--env-file $ENV_FILE}"

if [ -n "${BACKUP_DATABASE_URL:-}" ]; then
  pg_dump --format=custom --no-owner --no-privileges --file "$FILE" "$BACKUP_DATABASE_URL"
  pg_restore --list "$FILE" > /dev/null
else
  $COMPOSE exec -T postgres pg_dump -U adan --format=custom --no-owner --no-privileges adan > "$FILE"
  $COMPOSE exec -T postgres pg_restore --list < "$FILE" > /dev/null
fi
# El archivo se puede leer entero: si pg_restore --list falla, el backup no sirve
sha256sum "$FILE" > "$FILE.sha256"
echo "$FILE"
