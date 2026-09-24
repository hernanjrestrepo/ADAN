"""Core configuration — all settings from environment, zero hardcoding."""
from __future__ import annotations

import os
from pathlib import Path


def normalize_database_url(url: str) -> str:
    """PostgreSQL siempre con psycopg 3; acepta `postgres://` y `postgresql://`."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


class Settings:
    # Database
    DATABASE_URL: str = normalize_database_url(os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).parent.parent.parent / 'data' / 'adan.db'}"
    ))
    # Aplica las migraciones de Alembic al arrancar (las pruebas lo desactivan)
    AUTO_MIGRATE: bool = os.getenv("AUTO_MIGRATE", "true").lower() in ("1", "true", "yes")

    # JWT Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "adan-dev-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))  # 24h

    # Ollama / AI
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "qwen2.5:0.5b")
    AI_TIMEOUT_SECONDS: int = int(os.getenv("AI_TIMEOUT_SECONDS", "120"))

    # Embeddings del EMS: "local" (hash, sin red) u "ollama" (EMBEDDING_MODEL real)
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "local")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    # CORS
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # App
    APP_NAME: str = "ADÁN"
    APP_VERSION: str = "0.1.0"


# Dimensión fija de la columna pgvector: la de nomic-embed-text. Cambiarla exige una migración.
EMBEDDING_DIM = 768

settings = Settings()
