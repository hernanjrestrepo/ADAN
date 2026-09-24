"""Health check + basic metrics. Required by WO-001 acceptance criteria."""

import time

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db

router = APIRouter(tags=["health"])

_started_at = time.monotonic()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "uptime_seconds": round(time.monotonic() - _started_at, 2)}


@router.get("/health/deep")
def health_deep(
    db: Session = Depends(get_db), settings: Settings = Depends(get_settings)
) -> dict:
    """Verifies real connectivity to Postgres, Redis (via URL ping) and Ollama."""
    checks: dict[str, str] = {}

    try:
        db.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["postgres"] = f"error: {exc}"

    try:
        import redis

        r = redis.from_url(settings.redis_url)
        r.ping()
        checks["redis"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["redis"] = f"error: {exc}"

    try:
        resp = httpx.get(f"{settings.ollama_base_url}/api/version", timeout=3.0)
        checks["ollama"] = "ok" if resp.status_code == 200 else f"http {resp.status_code}"
    except Exception as exc:  # noqa: BLE001
        checks["ollama"] = f"error: {exc}"

    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return {"status": overall, "checks": checks}


@router.get("/metrics")
def metrics() -> dict:
    return {"uptime_seconds": round(time.monotonic() - _started_at, 2)}
