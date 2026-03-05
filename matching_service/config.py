"""Конфигурация Matching Service (stateless, без собственной БД)."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Matching Service."""

    app_name: str = "Matching Service"
    debug: bool = False

    # Внешние сервисы (по умолчанию — локальный запуск без Docker)
    auth_url: str = "http://localhost:8000"
    ideas_url: str = "http://localhost:8002"

    model_config = {"env_file": ".env", "env_prefix": "MATCH_"}


settings = Settings()

