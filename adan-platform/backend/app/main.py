"""FastAPI app factory. BP-0001 a BP-0009 (Fundamentos) viven aqui como configuracion base."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.config import get_settings
from app.errors import register_error_handlers
from app.logging_config import configure_logging
from app.routers.health import router as health_router

logger = logging.getLogger("adan")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.environment)

    app = FastAPI(
        title="ADAN API",
        description="Sistema Operativo Empresarial - Backend",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    app.include_router(health_router)
    app.include_router(auth_router)

    logger.info("ADAN API started (environment=%s)", settings.environment)
    return app


app = create_app()
