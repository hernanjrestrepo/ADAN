"""Core configuration — all settings from environment, zero hardcoding."""
from __future__ import annotations

import os
from pathlib import Path


DEFAULT_JWT_SECRET = "adan-dev-secret-change-in-production"


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    # Entorno: development | production (WO-093)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").strip().lower()

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).parent.parent.parent / 'data' / 'adan.db'}"
    )

    # JWT Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", DEFAULT_JWT_SECRET)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))  # 24h

    # Ollama / AI
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "qwen2.5:0.5b")
    AI_TIMEOUT_SECONDS: int = int(os.getenv("AI_TIMEOUT_SECONDS", "120"))

    # CORS
    CORS_ORIGINS: list[str] = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()
    ]

    # Seguridad / operación (WO-093)
    AUTH_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AUTH_RATE_LIMIT_PER_MINUTE", "20"))
    TRUST_PROXY_HEADERS: bool = _bool("TRUST_PROXY_HEADERS", False)
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    METRICS_ENABLED: bool = _bool("METRICS_ENABLED", True)

    # Database pool (solo PostgreSQL)
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))

    # EMS embeddings: "local" (hashing, sin dependencias) u "ollama" (semántico real)
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "local")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "128"))

    # App
    APP_NAME: str = "ADÁN"
    APP_VERSION: str = "1.0.0"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def docs_enabled(self) -> bool:
        return _bool("ENABLE_DOCS", not self.is_production)

    def validate(self) -> list[str]:
        """Errores de configuración que impiden arrancar en producción."""
        if not self.is_production:
            return []
        errors = []
        if self.JWT_SECRET == DEFAULT_JWT_SECRET or len(self.JWT_SECRET) < 32:
            errors.append("JWT_SECRET debe definirse con al menos 32 caracteres aleatorios")
        if self.DATABASE_URL.startswith("sqlite"):
            errors.append("DATABASE_URL debe apuntar a PostgreSQL en producción")
        if "*" in self.CORS_ORIGINS:
            errors.append("CORS_ORIGINS no puede ser '*' en producción (se envían credenciales)")
        return errors


settings = Settings()
