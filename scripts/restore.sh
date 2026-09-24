#!/usr/bin/env bash
# Restaura un backup de backup.sh. Reemplaza el contenido de la base: exige CONFIRM=si.
#
#   CONFIRM=si scripts/restore.sh backups/adan-XXXX.dump                      # vía docker compose
#   CONFIRM=si RESTORE_DATABASE_URL=postgresql://... scripts/restore.sh FILE  # conexión directa
set -euo pipefail
FILE="${1:?Uso: CONFIRM=si scripts/restore.sh <archivo.dump>}"
[ "${CONFIRM:-}" = "si" ] || { echo "Restaurar borra los datos actuales. Repite con CONFIRM=si" >&2; exit 1; }
sha256sum --check --status "$FILE.sha256" || { echo "La suma SHA-256 no coincide: backup dañado" >&2; exit 1; }
COMPOSE="docker compose -f ${COMPOSE_FILE:-docker-compose.prod.yml} ${ENV_FILE:+--env-file $ENV_FILE}"

if [ -n "${RESTORE_DATABASE_URL:-}" ]; then
  pg_restore --clean --if-exists --no-owner --no-privileges --exit-on-error --dbname "$RESTORE_DATABASE_URL" "$FILE"
else
  # Sin tráfico durante la restauración: se detiene el backend y se levanta al final
  $COMPOSE stop backend
  $COMPOSE exec -T postgres pg_restore -U adan --clean --if-exists --no-owner --no-privileges --exit-on-error --dbname adan < "$FILE"
  $COMPOSE start backend
fi
echo "Restaurado: $FILE"
