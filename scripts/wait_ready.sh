#!/usr/bin/env bash
# Espera a que el backend esté listo (/health/ready desde dentro de la red) y nginx responda.
set -euo pipefail
COMPOSE="${1:-docker compose -f docker-compose.prod.yml}"
for _ in $(seq 1 60); do
  if $COMPOSE exec -T backend python -c "import urllib.request,json; r=urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=3); print(json.load(r))" 2>/dev/null; then
    $COMPOSE exec -T frontend wget -qO /dev/null http://127.0.0.1:8080/ && exit 0
  fi
  sleep 3
done
echo "El backend no quedó listo" >&2
$COMPOSE logs --tail 50 backend >&2
exit 1
