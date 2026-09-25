"""Observabilidad (WO-093): identificador por petición, log de acceso y métricas Prometheus.

- Cada petición lleva un `X-Request-ID` (el que manda el cliente, si es válido, o uno nuevo).
  Aparece en la respuesta y en **todas** las líneas de log que se escriben mientras dura
  la petición, así se puede seguir una solicitud de punta a punta (trazas por correlación).
- `/metrics` expone contadores e histogramas en formato Prometheus: peticiones por ruta y
  código, latencia por ruta, llamadas al LLM por operación y resultado, y peticiones
  rechazadas por los límites.
"""
from __future__ import annotations

import logging
import os
import re
import time
import uuid
from contextvars import ContextVar

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
# Rutas de sondeo: se registran en DEBUG para no inundar el log
QUIET_PATHS = {"/health", "/health/ready", "/metrics"}

HTTP_REQUESTS = Counter(
    "adan_http_requests_total", "Peticiones HTTP atendidas", ["method", "route", "status"],
)
HTTP_LATENCY = Histogram(
    "adan_http_request_duration_seconds", "Latencia de las peticiones HTTP", ["method", "route"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120, 300),
)
LLM_LATENCY = Histogram(
    "adan_llm_call_duration_seconds", "Duración de las llamadas al LLM", ["operation", "outcome"],
    buckets=(0.5, 1, 2.5, 5, 10, 20, 30, 60, 90, 120, 180, 300),
)
RATE_LIMITED = Counter("adan_rate_limited_total", "Peticiones rechazadas por los límites", ["scope"])

access_logger = logging.getLogger("adan.access")


def new_request_id(incoming: str | None) -> str:
    if incoming and _VALID_REQUEST_ID.match(incoming):
        return incoming
    return uuid.uuid4().hex


def route_template(scope: dict) -> str:
    """La plantilla completa de la ruta (`/api/v1/nivel1/{company_id}/chat`), no la URL concreta:
    así no se crea una serie de métricas por cada id.

    FastAPI guarda en `route.path` la ruta relativa a su router (`/nivel1/{company_id}/chat`);
    el prefijo (`/api/v1`) se recupera de los primeros segmentos de la URL real, porque los
    prefijos de los routers de ADÁN son fijos.
    """
    route_path = getattr(scope.get("route"), "path", None)
    if not route_path:
        return "sin_ruta"
    actual = [seg for seg in scope.get("path", "").split("/") if seg]
    relative = [seg for seg in route_path.split("/") if seg]
    prefix = actual[: max(len(actual) - len(relative), 0)]
    return "/" + "/".join(prefix + relative) if (prefix or relative) else "/"


def record_request(method: str, route: str, status: int, duration: float, path: str, client: str) -> None:
    HTTP_REQUESTS.labels(method, route, str(status)).inc()
    HTTP_LATENCY.labels(method, route).observe(duration)
    level = logging.DEBUG if path in QUIET_PATHS else logging.INFO
    access_logger.log(level, f"{method} {route} {status}", extra={"extra_data": {
        "method": method, "route": route, "path": path, "status": status,
        "duration_ms": round(duration * 1000, 1), "client": client,
    }})


def metrics_payload() -> tuple[bytes, str]:
    """Con varios workers (PROMETHEUS_MULTIPROC_DIR), suma las métricas de todos los procesos."""
    if os.environ.get("PROMETHEUS_MULTIPROC_DIR"):
        from prometheus_client import CollectorRegistry, multiprocess
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        return generate_latest(registry), CONTENT_TYPE_LATEST
    return generate_latest(), CONTENT_TYPE_LATEST


class LLMTimer:
    """`with LLMTimer("chat"):` registra la duración y si la llamada falló."""

    def __init__(self, operation: str):
        self.operation = operation

    def __enter__(self):
        self.start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc, tb):
        outcome = "error" if exc_type else "ok"
        LLM_LATENCY.labels(self.operation, outcome).observe(time.monotonic() - self.start)
        return False
