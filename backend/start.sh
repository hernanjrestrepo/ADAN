#!/bin/sh
# Arranque del backend de ADÁN.
#   ENVIRONMENT=production → varios workers, sin --reload, cabeceras de proxy
#   WAIT_FOR_OLLAMA=true   → espera a que Ollama responda antes de arrancar
set -e

if [ "${WAIT_FOR_OLLAMA:-true}" = "true" ]; then
    echo "Waiting for Ollama at ${OLLAMA_BASE_URL:-http://ollama:11434}..."
    until python -c "import os, urllib.request; urllib.request.urlopen(os.environ.get('OLLAMA_BASE_URL', 'http://ollama:11434') + '/api/tags', timeout=3)" > /dev/null 2>&1; do
        sleep 2
    done
    echo "Ollama is ready."
fi

# Las migraciones también corren en el lifespan (con advisory lock), pero
# ejecutarlas aquí una vez evita que los workers compitan al arrancar.
python -c "from app.core.database import init_db; init_db()"

if [ "${ENVIRONMENT:-development}" = "production" ]; then
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 \
        --workers "${WEB_CONCURRENCY:-2}" \
        --proxy-headers --forwarded-allow-ips "${FORWARDED_ALLOW_IPS:-*}" \
        --no-access-log
else
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --no-access-log
fi
