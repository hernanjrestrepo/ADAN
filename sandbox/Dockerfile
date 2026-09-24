FROM python:3.12-slim

# Usuario sin privilegios; el código del usuario corre con él
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin sandbox
WORKDIR /srv
COPY sandbox.py .
USER 10001
EXPOSE 8100
HEALTHCHECK --interval=10s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8100/health', timeout=2)"
CMD ["python", "-I", "sandbox.py"]
