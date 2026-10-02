FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Usuario sin privilegios; data/ guarda SQLite (desarrollo) y archivos de TEF
RUN useradd --create-home --uid 10001 adan \
    && mkdir -p /app/data/files \
    && chmod +x start.sh \
    && chown -R adan:adan /app/data
USER adan

EXPOSE 8000

# Sin curl: la imagen no necesita paquetes del sistema (menos superficie de CVEs)
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=4)" || exit 1

CMD ["./start.sh"]
