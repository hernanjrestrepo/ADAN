"""Límites de peticiones (WO-097, S14; Redis en WO-093).

Ventana deslizante por clave. Con REDIS_URL la cuenta es compartida por todos los workers y
réplicas (script Lua atómico); sin Redis vive en la memoria del proceso, que alcanza para
una sola instancia o para pruebas.
"""
from __future__ import annotations

import logging
import threading
import time
import uuid
from collections import defaultdict, deque

from fastapi import Depends, HTTPException, Request

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.observability import RATE_LIMITED
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

    def ping(self) -> bool:
        return True


# Limpia lo vencido, cuenta y, si hay cupo y se pide, registra el intento. Devuelve la espera
# en segundos cuando no hay cupo, o "" cuando sí hay.
_SLIDING_WINDOW_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
if redis.call('ZCARD', key) >= limit then
  local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
  return tostring(tonumber(oldest[2]) + window - now)
end
if ARGV[5] == '1' then
  redis.call('ZADD', key, now, ARGV[4])
  redis.call('EXPIRE', key, math.ceil(window) + 1)
end
return ''
"""

logger = logging.getLogger(__name__)


class RedisSlidingWindowLimiter:
    """La misma ventana deslizante, en Redis. Si Redis falla, deja pasar y lo registra:
    la disponibilidad pesa más, y /health/ready reporta el problema."""

    PREFIX = "adan:rl:"

    def __init__(self, url: str):
        import redis
        self._redis = redis.Redis.from_url(url, socket_timeout=1, socket_connect_timeout=1)
        self._script = self._redis.register_script(_SLIDING_WINDOW_LUA)

    def _run(self, key: str, limit: int, window: float, record: bool) -> float | None:
        if limit <= 0:
            return None
        try:
            wait = self._script(keys=[self.PREFIX + key],
                                args=[time.time(), window, limit, uuid.uuid4().hex, "1" if record else "0"])
        except Exception as exc:  # noqa: BLE001
            logger.error("Límite no aplicado: Redis no responde (%s)", type(exc).__name__)
            return None
        wait = wait.decode() if isinstance(wait, bytes) else wait
        return max(1.0, float(wait)) if wait else None

    def hit(self, key: str, limit: int, window: float) -> float | None:
        return self._run(key, limit, window, record=True)

    def blocked_for(self, key: str, limit: int, window: float) -> float | None:
        return self._run(key, limit, window, record=False)

    def reset(self, key: str | None = None) -> None:
        if key is not None:
            self._redis.delete(self.PREFIX + key)
            return
        for found in self._redis.scan_iter(match=self.PREFIX + "*"):
            self._redis.delete(found)

    def ping(self) -> bool:
        try:
            return bool(self._redis.ping())
        except Exception:  # noqa: BLE001
            return False


def build_limiter(redis_url: str):
    return RedisSlidingWindowLimiter(redis_url) if redis_url else SlidingWindowLimiter()


limiter = build_limiter(settings.REDIS_URL)


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def too_many(retry_after: float, detail: str = "Demasiadas solicitudes; intenta más tarde",
             scope: str = "api") -> HTTPException:
    RATE_LIMITED.labels(scope).inc()
    return HTTPException(status_code=429, detail=detail, headers={"Retry-After": str(int(retry_after) + 1)})


def llm_user(current_user: User = Depends(get_current_user)) -> User:
    """Usuario autenticado, con un tope de llamadas por minuto a endpoints que usan el LLM."""
    wait = limiter.hit(f"llm:{current_user.id}", settings.LLM_RATE_LIMIT_PER_MINUTE, 60)
    if wait:
        raise too_many(wait, "Demasiadas solicitudes al modelo; espera un momento", scope="llm")
    return current_user
