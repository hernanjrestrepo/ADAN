"""ADÁN Backend — FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.router import router as v1_router
from app.ems.api import router as ems_router
from app.tef.api import router as tef_router
from app.agents.api import router as agents_router
from app.agents.board_api import router as board_router
from app.oos.api import router as oos_router
from app.dka.api import router as dka_router
from app.integrations.api import router as integrations_router
from app.voice.api import router as voice_router
from app.omnichannel.api import router as omnichannel_router
from app.core.config import settings
from app.core.database import get_db, init_db
from app.core.logging import setup_logging
from app.core.observability import RequestContextMiddleware, metrics_response_body
from app.core.security import SecurityHeadersMiddleware

logger = setup_logging(settings.LOG_LEVEL)

_config_errors = settings.validate()
if _config_errors:
    # Fallar al arrancar es preferible a correr en producción con secretos por defecto
    raise RuntimeError("Configuración inválida para producción: " + "; ".join(_config_errors))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    logger.info("ADÁN backend starting up", extra={"extra_data": {"environment": settings.ENVIRONMENT}})
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("ADÁN backend shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

# Middlewares (el último agregado es el más externo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestContextMiddleware)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.warning("Integrity error", extra={"extra_data": {"error": str(exc.orig)[:300]}})
    return JSONResponse(
        status_code=409,
        content={"detail": "La operación viola una restricción de datos (referencia inexistente o duplicado)"},
    )


# API routes
app.include_router(v1_router)
app.include_router(ems_router)
app.include_router(tef_router)
app.include_router(agents_router)
app.include_router(board_router)
app.include_router(oos_router)
app.include_router(dka_router)
app.include_router(integrations_router)
app.include_router(voice_router)
app.include_router(omnichannel_router)


@app.get("/health")
def health():
    """Liveness: el proceso responde."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    """Readiness: base de datos accesible y esquema en la última migración."""
    from alembic.runtime.migration import MigrationContext
    from alembic.script import ScriptDirectory

    from app.core.migrations import alembic_config

    checks: dict[str, str] = {}
    try:
        conn = db.connection()
        conn.execute(text("SELECT 1"))
        current = MigrationContext.configure(conn).get_current_revision()
        head = ScriptDirectory.from_config(alembic_config()).get_current_head()
        checks["database"] = "ok"
        checks["migrations"] = "ok" if current == head else f"pending ({current} -> {head})"
    except Exception as exc:  # noqa: BLE001 — se reporta, no se propaga
        logger.warning("Readiness check failed", extra={"extra_data": {"error": str(exc)[:300]}})
        checks["database"] = "unavailable"

    ready = all(v == "ok" for v in checks.values())
    return JSONResponse(status_code=200 if ready else 503, content={"status": "ready" if ready else "not_ready", "checks": checks})


if settings.METRICS_ENABLED:
    @app.get("/metrics", include_in_schema=False)
    def metrics():
        body, content_type = metrics_response_body()
        return Response(content=body, media_type=content_type)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.docs_enabled else None,
        "health": "/health",
    }
