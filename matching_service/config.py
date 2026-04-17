"""Конфигурация Matching Service."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Matching Service."""

    app_name: str = "Matching Service"
    debug: bool = False

    # Database (в Docker: MATCH_DATABASE_URL)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/matching_db"

    # Каталог идей (Idea Service) — подбор и приглашения по ID из каталога
    idea_service_url: str = "http://localhost:8002"

    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"

    model_config = {"env_file": ".env", "env_prefix": "MATCH_"}


settings = Settings()

