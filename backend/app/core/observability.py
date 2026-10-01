"""Observabilidad (WO-093): request ID, access log estructurado y métricas.

- Cada request recibe un `X-Request-ID` (se respeta el entrante si es válido)
  que aparece en todos los logs emitidos durante esa request.
- Métricas Prometheus en `/metrics`, etiquetadas por plantilla de ruta
  (`/oos/workorders/{work_order_id}`), nunca por la URL concreta, para no
  disparar la cardinalidad.
"""
from __future__ import annotations

import json
import logging
import re
import time
import uuid
from contextvars import ContextVar

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.types import ASGIApp, Message, Receive, Scope, Send

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")

HTTP_REQUESTS = Counter(
    "adan_http_requests_total",
    "Requests HTTP atendidas",
    ["method", "route", "status"],
)
HTTP_LATENCY = Histogram(
    "adan_http_request_duration_seconds",
    "Latencia de requests HTTP",
    ["method", "route"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120),
)

access_logger = logging.getLogger("adan.access")
error_logger = logging.getLogger("adan.errors")


def current_request_id() -> str | None:
    return request_id_var.get()


class RequestContextMiddleware:
    """Middleware ASGI puro (no bufferiza respuestas en streaming/SSE)."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = _header(scope, b"x-request-id")
        request_id = incoming if incoming and _VALID_REQUEST_ID.match(incoming) else uuid.uuid4().hex
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        status_code = 500
        response_started = False

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status_code = message["status"]
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            # Error no controlado: se registra con su request_id y el cliente
            # recibe un 500 genérico (sin detalles internos) que lo incluye.
            error_logger.exception("Unhandled error")
            if not response_started:
                body = json.dumps({"detail": "Error interno", "request_id": request_id}).encode()
                await send_wrapper({
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())],
                })
                await send_wrapper({"type": "http.response.body", "body": body})
        finally:
            duration = time.perf_counter() - start
            route = getattr(scope.get("route"), "path", None) or "unmatched"
            method = scope["method"]
            if route != "/metrics":
                HTTP_REQUESTS.labels(method, route, str(status_code)).inc()
                HTTP_LATENCY.labels(method, route).observe(duration)
            access_logger.info(
                "%s %s %s", method, scope["path"], status_code,
                extra={"extra_data": {
                    "method": method,
                    "path": scope["path"],
                    "route": route,
                    "status": status_code,
                    "duration_ms": round(duration * 1000, 1),
                }},
            )
            request_id_var.reset(token)


def metrics_response_body() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST


def _header(scope: Scope, name: bytes) -> str | None:
    for key, value in scope.get("headers", []):
        if key == name:
            return value.decode("latin-1")
    return None
