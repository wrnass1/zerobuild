"""
Auth Service — управление пользователями и авторизация (JWT).

Эндпоинты:
- POST /register — регистрация
- POST /login    — вход (JWT)
- GET  /profile — профиль (требуется JWT)
- PUT  /profile — обновление профиля (требуется JWT)

Документация API: Swagger UI — /docs, ReDoc — /redoc.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from database import init_db
import models  # noqa: F401 — регистрируем модели до create_all
from routers import auth_router, profile_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создание таблиц при старте."""
    await init_db()
    yield


app = FastAPI(
    title="Auth Service",
    description=(
        "Сервис авторизации платформы pet-проектов: регистрация, вход по JWT, "
        "хранение и редактирование профиля (имя, email, стек технологий, уровень, описание, проекты)."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Токен из POST /login или POST /register",
        }
    }
    for path, path_item in openapi_schema.get("paths", {}).items():
        if "/profile" in path:
            for method in ("get", "put", "post", "delete", "patch"):
                if method in path_item and isinstance(path_item[method], dict):
                    path_item[method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(profile_router.router)


@app.get("/health", tags=["Служебные"])
async def health():
    """Проверка доступности сервиса."""
    return {"status": "ok", "service": "auth"}
