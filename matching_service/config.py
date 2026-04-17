"""Конфигурация Matching Service (stateless, без собственной БД)."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Matching Service."""

    app_name: str = "Matching Service"
    debug: bool = False

    # Внешние сервисы (в Docker задаются MATCH_AUTH_URL / MATCH_IDEAS_URL)
    auth_url: str = "http://localhost:8000"
    ideas_url: str = "http://localhost:8002"

    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"

    model_config = {"env_file": ".env", "env_prefix": "MATCH_"}


settings = Settings()

