#!/usr/bin/env bash
# Despliegue con backup previo, migraciones y verificación de salud (WO-093).
#
#   scripts/deploy.sh [etiqueta]    # por defecto, el commit actual
# Rollback: scripts/rollback.sh <etiqueta-anterior> [revision-de-alembic]
set -euo pipefail
TAG="${1:-$(git rev-parse --short HEAD)}"
ENV_FILE="${ENV_FILE:-.env.prod}"
COMPOSE="docker compose -f docker-compose.prod.yml --env-file $ENV_FILE"
export ADAN_TAG="$TAG"

echo "1/5 Construyendo imágenes $TAG"
$COMPOSE build

echo "2/5 Backup previo"
if $COMPOSE ps --status running postgres | grep -q postgres; then
  ENV_FILE="$ENV_FILE" scripts/backup.sh backups
else
  echo "    (primera instalación: no hay base que respaldar)"
fi

echo "3/5 Migraciones"
$COMPOSE up -d postgres redis
$COMPOSE run --rm migrate

echo "4/5 Arranque"
# DEPLOY_SERVICES limita los servicios (CI no levanta Ollama); vacío = todos
# shellcheck disable=SC2086
$COMPOSE up -d ${DEPLOY_SERVICES:-}

echo "5/5 Verificación"
scripts/wait_ready.sh "$COMPOSE"
echo "$TAG" > .deployed_tag
echo "Desplegado $TAG"
