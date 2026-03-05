"""Конфигурация Gateway."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """URL сервисов для проксирования."""

    auth_url: str = "http://localhost:8000"
    ideas_url: str = "http://localhost:8002"
    kanban_url: str = "http://localhost:8003"
    matching_url: str = "http://localhost:8001"

    model_config = {"env_file": ".env", "env_prefix": "GATEWAY_"}


settings = Settings()
