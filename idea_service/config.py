"""Конфигурация Idea Service."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    app_name: str = "Idea Service"
    debug: bool = False

    # Database (в Docker: IDEA_DATABASE_URL)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/idea_db"

    # JWT — должны совпадать с Auth Service (AUTH_SECRET_KEY, AUTH_ALGORITHM)
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"

    model_config = {"env_file": ".env", "env_prefix": "IDEA_"}


settings = Settings()
