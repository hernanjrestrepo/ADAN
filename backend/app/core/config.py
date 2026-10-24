"""Core configuration — all settings from environment, zero hardcoding."""
from __future__ import annotations

import logging
import os
import secrets
from pathlib import Path

logger = logging.getLogger(__name__)


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

    # development | test | production. En producción la app no arranca con secretos débiles.
    ADAN_ENV: str = os.getenv("ADAN_ENV", "development").lower()

    # JWT Auth. Sin JWT_SECRET, fuera de producción se genera uno aleatorio por proceso:
    # nunca hay un secreto público por defecto (hallazgo S12). Las sesiones no sobreviven
    # a un reinicio, lo cual es aceptable en desarrollo.
    JWT_SECRET: str = os.getenv("JWT_SECRET") or secrets.token_urlsafe(48)
    JWT_SECRET_IS_EPHEMERAL: bool = not os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))  # 24h

    # Ollama / AI
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "qwen2.5:0.5b")
    AI_TIMEOUT_SECONDS: int = int(os.getenv("AI_TIMEOUT_SECONDS", "120"))

    # Enrutamiento de modelos (WO-099, AD-DEC-0002 decisión 3): Ollama para lo simple,
    # Anthropic según la complejidad. Sin ANTHROPIC_API_KEY todo va a Ollama (degradado).
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    # Proveedor de nube: "auto" (Claude si hay clave, si no Kimi), "anthropic" o "kimi"
    LLM_CLOUD_PROVIDER: str = os.getenv("LLM_CLOUD_PROVIDER", "auto").strip().lower()
    # Kimi (Moonshot), compatible con OpenAI: la misma cuenta de Xmart Travel. Un solo modelo para todos los niveles.
    KIMI_API_KEY: str = os.getenv("KIMI_API_KEY", "")
    KIMI_BASE_URL: str = os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1")
    KIMI_MODEL: str = os.getenv("KIMI_MODEL", "kimi-k2.6")
    KIMI_PRICE_INPUT: float = float(os.getenv("KIMI_PRICE_INPUT", "0.95"))   # USD por millón (lista, oct-2026)
    KIMI_PRICE_OUTPUT: float = float(os.getenv("KIMI_PRICE_OUTPUT", "4.0"))

    # CSI (AD-000 §3): inteligencia externa del ecosistema Paradixe. Sin URL, ADÁN no inventa datos
    # externos: solo verifica las fuentes que aporta el cliente (WO-108).
    CSI_BASE_URL: str = os.getenv("CSI_BASE_URL", "").rstrip("/")
    CSI_API_KEY: str = os.getenv("CSI_API_KEY", "")
    # Comunidad: correos de los curadores de Paradixe que marcan las Selecciones Paradixe (separados por comas)
    PARADIXE_CURATORS: str = os.getenv("PARADIXE_CURATORS", "")

    # @pples (1 @pple = USD 1) y su pasarela. "simulador" mientras no haya llaves de Wompi; con llaves de producción
    # (pub_prod_) no se cobra hasta encender PAYMENTS_LIVE, con aprobación de Hernán.
    PUBLIC_URL: str = os.getenv("PUBLIC_URL", "http://localhost:5173").rstrip("/")
    PAYMENTS_PROVIDER: str = os.getenv("PAYMENTS_PROVIDER", "simulador")
    PAYMENTS_LIVE: bool = os.getenv("PAYMENTS_LIVE", "false").lower() in ("1", "true", "yes")
    WOMPI_PUBLIC_KEY: str = os.getenv("WOMPI_PUBLIC_KEY", "")
    WOMPI_PRIVATE_KEY: str = os.getenv("WOMPI_PRIVATE_KEY", "")
    WOMPI_INTEGRITY_SECRET: str = os.getenv("WOMPI_INTEGRITY_SECRET", "")
    WOMPI_EVENTS_SECRET: str = os.getenv("WOMPI_EVENTS_SECRET", "")
    WOMPI_FEE_RATE: float = float(os.getenv("WOMPI_FEE_RATE", "0.0265"))
    WOMPI_FEE_FIXED_COP: int = int(os.getenv("WOMPI_FEE_FIXED_COP", "700"))
    IVA_RATE: float = float(os.getenv("IVA_RATE", "0.19"))
    APPLE_TRM: int = int(os.getenv("APPLE_TRM", "4000"))  # COP por USD para cobrar las @pples
    # Exigir el pago del Nivel con @pples antes de trabajarlo (se enciende cuando la pasarela esté lista)
    APPLES_REQUIRED: bool = os.getenv("APPLES_REQUIRED", "false").lower() in ("1", "true", "yes")
    LLM_MODEL_STANDARD: str = os.getenv("LLM_MODEL_STANDARD", "claude-sonnet-5")
    LLM_MODEL_COMPLEX: str = os.getenv("LLM_MODEL_COMPLEX", "claude-opus-5")
    LLM_MODEL_FAST: str = os.getenv("LLM_MODEL_FAST", "claude-haiku-4-5")

    # Embeddings del EMS: "local" (hash, sin red) u "ollama" (EMBEDDING_MODEL real)
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "local")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    # Cookie de sesión solo por HTTPS. Por defecto, en producción. Desactivarla solo para
    # pruebas locales del stack de producción sin TLS (p. ej. la prueba de humo de CI).
    SESSION_COOKIE_SECURE: bool = os.getenv(
        "SESSION_COOKIE_SECURE", "true" if os.getenv("ADAN_ENV", "development").lower() == "production" else "false"
    ).lower() in ("1", "true", "yes")

    # Cifrado de credenciales de conectores (Fernet, 32 bytes en base64 url-safe)
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")

    # Límites (0 desactiva el límite correspondiente)
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "600"))     # por IP
    LLM_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("LLM_RATE_LIMIT_PER_MINUTE", "30"))  # por usuario
    MAX_BODY_BYTES: int = int(os.getenv("MAX_BODY_BYTES", str(1024 * 1024)))
    MAX_UPLOAD_BODY_BYTES: int = int(os.getenv("MAX_UPLOAD_BODY_BYTES", str(60 * 1024 * 1024)))
    LOGIN_MAX_FAILURES: int = int(os.getenv("LOGIN_MAX_FAILURES", "5"))  # por IP + email, en 15 min
    REGISTER_PER_IP_PER_HOUR: int = int(os.getenv("REGISTER_PER_IP_PER_HOUR", "20"))

    # Sandbox aislado para ejecutar código (servicio sandbox/). Vacío: python_sandbox apagada.
    SANDBOX_URL: str = os.getenv("SANDBOX_URL", "")
    SANDBOX_TOKEN: str = os.getenv("SANDBOX_TOKEN", "")

    # Redis para los límites compartidos entre réplicas (vacío: límites en memoria del proceso)
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    # Protege /metrics con `Authorization: Bearer <METRICS_TOKEN>` (vacío: abierto a la red interna)
    METRICS_TOKEN: str = os.getenv("METRICS_TOKEN", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Hosts permitidos para las llamadas salientes de herramientas y conectores
    # (vacío: cualquier host público). El proxy de salida se configura con HTTPS_PROXY.
    OUTBOUND_ALLOWED_HOSTS: list[str] = [
        h.strip().lower() for h in os.getenv("OUTBOUND_ALLOWED_HOSTS", "").split(",") if h.strip()
    ]

    # CORS
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # App
    APP_NAME: str = "ADÁN"
    APP_VERSION: str = "0.1.0"


def production_problems(cfg: "Settings") -> list[str]:
    """Qué impide arrancar en producción. Vacío si todo está en orden."""
    problems = []
    if cfg.JWT_SECRET_IS_EPHEMERAL or len(cfg.JWT_SECRET) < 32:
        problems.append("JWT_SECRET debe definirse, con al menos 32 caracteres")
    if not cfg.ENCRYPTION_KEY:
        problems.append("ENCRYPTION_KEY debe definirse (Fernet.generate_key())")
    if cfg.DATABASE_URL.startswith("sqlite"):
        problems.append("DATABASE_URL debe ser PostgreSQL")
    if ":adan-dev@" in cfg.DATABASE_URL:
        problems.append("La contraseña de PostgreSQL no puede ser la de desarrollo (POSTGRES_PASSWORD)")
    if "*" in cfg.CORS_ORIGINS:
        problems.append("CORS_ORIGINS no puede ser '*'")
    if cfg.SANDBOX_URL and len(cfg.SANDBOX_TOKEN) < 32:
        problems.append("Con SANDBOX_URL, SANDBOX_TOKEN debe tener al menos 32 caracteres")
    return problems


def check_settings(cfg: "Settings") -> None:
    """En producción, falla si la configuración es insegura; fuera de ella, avisa."""
    problems = production_problems(cfg)
    if cfg.ADAN_ENV == "production" and problems:
        raise RuntimeError("Configuración insegura para producción: " + "; ".join(problems))
    if cfg.JWT_SECRET_IS_EPHEMERAL and cfg.ADAN_ENV != "test":
        logger.warning("JWT_SECRET no definido: se usa uno aleatorio; las sesiones se pierden al reiniciar")


# Dimensión fija de la columna pgvector: la de nomic-embed-text. Cambiarla exige una migración.
EMBEDDING_DIM = 768

settings = Settings()
