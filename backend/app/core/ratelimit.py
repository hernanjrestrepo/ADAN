"""Límites de peticiones en memoria (WO-097, S14).

Ventana deslizante por clave. Vale para un proceso: con varios workers o réplicas cada uno
lleva su cuenta. Pasar a Redis cuando haya más de una réplica (WO-093).
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import Depends, HTTPException, Request

from app.core.auth import get_current_user
from app.core.config import settings
from app.models.models import User


class SlidingWindowLimiter:
    def __init__(self):
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def _prune(self, key: str, window: float, now: float) -> deque:
        hits = self._hits[key]
        while hits and hits[0] <= now - window:
            hits.popleft()
        return hits

    def hit(self, key: str, limit: int, window: float) -> float | None:
        """Registra un intento. Devuelve None si se permite, o los segundos a esperar si no."""
        if limit <= 0:
            return None
        now = time.monotonic()
        with self._lock:
            hits = self._prune(key, window, now)
            if len(hits) >= limit:
                return max(1.0, hits[0] + window - now)
            hits.append(now)
            return None

    def blocked_for(self, key: str, limit: int, window: float) -> float | None:
        """Como `hit`, pero sin registrar: para bloquear antes de verificar una contraseña."""
        if limit <= 0:
            return None
        now = time.monotonic()
        with self._lock:
            hits = self._prune(key, window, now)
            if len(hits) >= limit:
                return max(1.0, hits[0] + window - now)
            return None

    def reset(self, key: str | None = None) -> None:
        with self._lock:
            if key is None:
                self._hits.clear()
            else:
                self._hits.pop(key, None)


limiter = SlidingWindowLimiter()


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def too_many(retry_after: float, detail: str = "Demasiadas solicitudes; intenta más tarde") -> HTTPException:
    return HTTPException(status_code=429, detail=detail, headers={"Retry-After": str(int(retry_after) + 1)})


def llm_user(current_user: User = Depends(get_current_user)) -> User:
    """Usuario autenticado, con un tope de llamadas por minuto a endpoints que usan el LLM."""
    wait = limiter.hit(f"llm:{current_user.id}", settings.LLM_RATE_LIMIT_PER_MINUTE, 60)
    if wait:
        raise too_many(wait, "Demasiadas solicitudes al modelo; espera un momento")
    return current_user
