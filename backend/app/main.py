"""ADÁN Backend — FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
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
from app.core.config import settings
from app.core.database import init_db, engine
from app.core.logging import setup_logging

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    logger.info("ADÁN backend starting up")
    init_db()
    logger.info("Database initialized (%s)", engine.dialect.name)
    yield
    logger.info("ADÁN backend shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

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
