"""ADÁN Backend — FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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
from app.core.database import init_db, engine
from app.core.logging import setup_logging
from app.core.ratelimit import client_ip, limiter

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    logger.info("ADÁN backend starting up (%s)", settings.ADAN_ENV)
    check_settings(settings)
    init_db()
    logger.info("Database initialized (%s)", engine.dialect.name)
    yield
    logger.info("ADÁN backend shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

@app.middleware("http")
async def security_guards(request: Request, call_next):
    """Límite de tamaño del cuerpo, límite de peticiones por IP y cabeceras de seguridad (WO-097)."""
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > settings.MAX_BODY_BYTES:
        return JSONResponse(status_code=413, content={"detail": "La solicitud es demasiado grande"})
    wait = limiter.hit(f"ip:{client_ip(request)}", settings.RATE_LIMIT_PER_MINUTE, 60)
    if wait:
        return JSONResponse(status_code=429, content={"detail": "Demasiadas solicitudes; intenta más tarde"},
                            headers={"Retry-After": str(int(wait) + 1)})
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
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
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
