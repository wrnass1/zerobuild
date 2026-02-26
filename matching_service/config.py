"""Конфигурация Matching Service."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Matching Service."""

    app_name: str = "Matching Service"
    debug: bool = False

    # Database (в Docker: MATCH_DATABASE_URL)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/matching_db"

    model_config = {"env_file": ".env", "env_prefix": "MATCH_"}


settings = Settings()

