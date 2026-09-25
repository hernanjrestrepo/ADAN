#!/usr/bin/env bash
# Vuelve a una versión anterior (WO-093).
#
#   scripts/rollback.sh <etiqueta-anterior> [revision-de-alembic]
#
# Si la versión nueva agregó migraciones, pasa la revisión de la versión anterior: se
# revierte con el código NUEVO (que conoce las migraciones) antes de cambiar las imágenes.
# Si una migración no se puede revertir, restaura el backup previo (scripts/restore.sh).
set -euo pipefail
TARGET="${1:?Uso: scripts/rollback.sh <etiqueta-anterior> [revision]}"
REVISION="${2:-}"
ENV_FILE="${ENV_FILE:-.env.prod}"
COMPOSE="docker compose -f docker-compose.prod.yml --env-file $ENV_FILE"

if [ -n "$REVISION" ]; then
  echo "Revirtiendo migraciones hasta $REVISION con la versión actual"
  ADAN_TAG="$(cat .deployed_tag)" $COMPOSE run --rm migrate alembic downgrade "$REVISION"
fi
echo "Volviendo a $TARGET"
ADAN_TAG="$TARGET" $COMPOSE up -d --no-build backend frontend sandbox
scripts/wait_ready.sh "$COMPOSE"
echo "$TARGET" > .deployed_tag
echo "Rollback a $TARGET listo"
