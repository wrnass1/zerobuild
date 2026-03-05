"""Конфигурация Idea Service."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    app_name: str = "Idea Service"
    debug: bool = False

    # Database (в Docker: IDEA_DATABASE_URL)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/idea_db"

    model_config = {"env_file": ".env", "env_prefix": "IDEA_"}


settings = Settings()
