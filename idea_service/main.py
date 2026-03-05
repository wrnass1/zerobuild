"""
Idea Service — каталог идей проектов.

Эндпоинты:
- GET    /ideas       — список с фильтрами (стек, сложность, поиск по названию)
- POST   /ideas       — создать идею
- GET    /ideas/{id}  — получить идею
- PUT    /ideas/{id}  — обновить идею
- DELETE /ideas/{id}  — удалить идею

Документация API: Swagger UI — /docs, ReDoc — /redoc.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
import models  # noqa: F401 — регистрируем модели до create_all
from routers import ideas_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создание таблиц при старте."""
    await init_db()
    yield


app = FastAPI(
    title="Idea Service",
    description=(
        "Каталог идей проектов: создание, просмотр, фильтрация по стеку и сложности, "
        "поиск по названию, редактирование и удаление."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ideas_router.router)


@app.get("/health", tags=["Служебные"])
async def health():
    """Проверка доступности сервиса."""
    return {"status": "ok", "service": "ideas"}
