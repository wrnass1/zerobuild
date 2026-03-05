"""Конфигурация Kanban Service."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    app_name: str = "Kanban Service"
    debug: bool = False

    # Database (в Docker: KANBAN_DATABASE_URL)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/kanban_db"

    model_config = {"env_file": ".env", "env_prefix": "KANBAN_"}


settings = Settings()
