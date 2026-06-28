from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE: Path = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """Application settings loaded from backend/.env."""

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

    # Keep configuration source explicit so app startup works from any cwd.
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")


settings = Settings()
