"""ADÁN Backend — FastAPI application entry point."""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

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
from app.core.config import check_settings, settings
from app.core.database import engine, get_db, init_db
from app.core.health import readiness_checks
from app.core.logging import setup_logging
from app.core.observability import (
    RATE_LIMITED, metrics_payload, new_request_id, record_request, request_id_var, route_template,
)
from app.core.ratelimit import client_ip, limiter

logger = setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    logger.info("ADÁN backend starting up (%s)", settings.ADAN_ENV)
    check_settings(settings)
    init_db()
    logger.info("Database initialized (%s)", engine.dialect.name)
    yield
    logger.info("ADÁN backend shutting down")


# En producción no se publica la documentación interactiva de la API
_docs = settings.ADAN_ENV != "production"
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if _docs else None,
    redoc_url="/redoc" if _docs else None,
    openapi_url="/openapi.json" if _docs else None,
)

@app.middleware("http")
async def security_guards(request: Request, call_next):
    """Límite de tamaño del cuerpo, límite de peticiones por IP y cabeceras de seguridad (WO-097)."""
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > settings.MAX_BODY_BYTES:
        RATE_LIMITED.labels("body").inc()
        return JSONResponse(status_code=413, content={"detail": "La solicitud es demasiado grande"})
    wait = limiter.hit(f"ip:{client_ip(request)}", settings.RATE_LIMIT_PER_MINUTE, 60)
    if wait:
        RATE_LIMITED.labels("ip").inc()
        return JSONResponse(status_code=429, content={"detail": "Demasiadas solicitudes; intenta más tarde"},
                            headers={"Retry-After": str(int(wait) + 1)})
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    return response


@app.middleware("http")
async def observability(request: Request, call_next):
    """X-Request-ID, log de acceso y métricas de cada petición (WO-093). Es el middleware más externo."""
    request_id = new_request_id(request.headers.get("x-request-id"))
    token = request_id_var.set(request_id)
    start = time.monotonic()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
    except Exception:
        # El request_id aún está en contexto: queda en el log y el cliente lo recibe para reportarlo
        logger.exception("Error no controlado")
        response = JSONResponse(status_code=500, content={"detail": "Error interno", "request_id": request_id})
    finally:
        record_request(request.method, route_template(request.scope), status, time.monotonic() - start,
                       request.url.path, client_ip(request))
        request_id_var.reset(token)
    response.headers["X-Request-ID"] = request_id
    return response


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """Liveness: el proceso responde. No toca dependencias."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/health/ready")
def ready(db: Session = Depends(get_db)):
    """Readiness: base de datos accesible y migraciones al día. Ollama y Redis se informan.

    Sin LLM la app sigue sirviendo sesión, empresas y datos, así que Ollama caído se
    reporta como degradado y no saca al backend de servicio.
    """
    checks, ready_ = readiness_checks(db)
    return JSONResponse(status_code=200 if ready_ else 503,
                        content={"status": "ready" if ready_ else "not_ready", "checks": checks})


@app.get("/metrics", include_in_schema=False)
def metrics(request: Request):
    """Métricas Prometheus. Con METRICS_TOKEN definido exige `Authorization: Bearer <token>`."""
    if settings.METRICS_TOKEN and request.headers.get("authorization") != f"Bearer {settings.METRICS_TOKEN}":
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    payload, content_type = metrics_payload()
    return Response(content=payload, media_type=content_type)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
