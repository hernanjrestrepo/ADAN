"""Shared config for the AI runtime. Deliberately separate from app/config.py (backend) -
sin acoplamiento directo entre /backend y /ai fuera de contratos (Plan Maestro SS3.2).
Same DATABASE_URL/REDIS_URL/OLLAMA_BASE_URL values, read independently."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AiSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://adan:adan_dev_password@localhost:5436/adan"
    redis_url: str = "redis://localhost:6382/0"
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama3.2:1b"  # modelo pequeno para desarrollo/pruebas rapidas


@lru_cache
def get_ai_settings() -> AiSettings:
    return AiSettings()
