"""Configuration by environment. BP-0003 (AD-002 regla 1.7 - todo tiene version/config declarada)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql+psycopg://adan:adan_dev_password@localhost:5436/adan"
    redis_url: str = "redis://localhost:6382/0"
    ollama_base_url: str = "http://localhost:11434"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
