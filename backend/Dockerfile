# Etapas: deps → development (docker-compose.yml) y production (docker-compose.prod.yml)
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

FROM base AS deps
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# Desarrollo: recarga automática y espera a Ollama (start.sh)
FROM base AS development
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY --from=deps /install /usr/local
COPY . .
RUN chmod +x start.sh && mkdir -p /app/data
EXPOSE 8000
CMD ["./start.sh"]

# Producción: usuario sin privilegios, sin recarga, varios workers. Las migraciones las corre
# el servicio `migrate` antes de arrancar (AUTO_MIGRATE=false).
FROM base AS production
RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin adan
COPY --from=deps /install /usr/local
COPY --chown=adan:adan alembic.ini ./
COPY --chown=adan:adan migrations ./migrations
COPY --chown=adan:adan app ./app
USER adan
ENV ADAN_ENV=production \
    AUTO_MIGRATE=false \
    WEB_CONCURRENCY=2 \
    PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"
# --proxy-headers: la IP real llega por X-Forwarded-For desde nginx (el backend no se publica)
# Las métricas de cada worker se escriben en PROMETHEUS_MULTIPROC_DIR y /metrics las suma
CMD ["sh", "-c", "rm -rf \"$PROMETHEUS_MULTIPROC_DIR\" && mkdir -p \"$PROMETHEUS_MULTIPROC_DIR\" && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${WEB_CONCURRENCY} --proxy-headers --forwarded-allow-ips='*'"]
