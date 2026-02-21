"""Конфигурация Auth Service."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    app_name: str = "Auth Service"
    debug: bool = False

    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database (в Docker: AUTH_DATABASE_URL)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/auth_db"

    model_config = {"env_file": ".env", "env_prefix": "AUTH_"}


settings = Settings()
