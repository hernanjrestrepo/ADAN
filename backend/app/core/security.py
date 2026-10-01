"""Endurecimiento HTTP (WO-093): cabeceras de seguridad y rate limiting."""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings

_SECURITY_HEADERS = [
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"strict-origin-when-cross-origin"),
    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
    (b"cross-origin-opener-policy", b"same-origin"),
]
# La API solo sirve JSON: ningún recurso activo debe cargarse desde sus respuestas.
# /docs (Swagger UI) carga scripts de un CDN, por eso queda fuera de esta CSP.
_API_CSP = (b"content-security-policy", b"default-src 'none'; frame-ancestors 'none'")
_DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        extra = list(_SECURITY_HEADERS)
        if not scope["path"].startswith(_DOCS_PATHS):
            extra.append(_API_CSP)
        if settings.is_production:
            extra.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains"))

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                message["headers"] = list(message.get("headers", [])) + extra
            await send(message)

        await self.app(scope, receive, send_wrapper)


def client_ip(request: Request) -> str:
    """IP del cliente; detrás de un proxy de confianza usa X-Forwarded-For."""
    if settings.TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class SlidingWindowRateLimiter:
    """Límite de requests por clave en una ventana deslizante (en memoria).

    Por proceso: con varios workers el límite efectivo se multiplica por el
    número de workers (aceptable para frenar fuerza bruta en login/registro).
    """

    def __init__(self, window_seconds: float = 60.0):
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def hit(self, key: str, limit: int) -> float | None:
        """Registra un intento; devuelve segundos de espera si se excede."""
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] >= self.window:
                hits.popleft()
            if len(hits) >= limit:
                return self.window - (now - hits[0])
            hits.append(now)
            return None

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


auth_rate_limiter = SlidingWindowRateLimiter()


def limit_auth_attempts(request: Request) -> None:
    """Dependencia FastAPI para endpoints de autenticación."""
    limit = settings.AUTH_RATE_LIMIT_PER_MINUTE
    if limit <= 0:
        return
    retry_after = auth_rate_limiter.hit(f"{request.url.path}:{client_ip(request)}", limit)
    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos. Intenta de nuevo en un minuto.",
            headers={"Retry-After": str(max(1, int(retry_after)))},
        )
