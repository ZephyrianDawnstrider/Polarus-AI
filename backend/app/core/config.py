from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE: Path = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """Application settings loaded from backend/.env and process env vars."""

    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    HOST: str
    PORT: int

    DATABASE_URL: str

    REDIS_HOST: str
    REDIS_PORT: int

    OLLAMA_URL: str
    DEFAULT_MODEL: str

    # Keep the env path absolute so startup works from any current directory.
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached settings instance for application-wide reuse."""

    return Settings()


# Singleton settings object imported by the application.
settings: Settings = get_settings()
