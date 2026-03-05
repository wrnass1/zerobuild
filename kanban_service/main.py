"""
Kanban Service — доски и задачи.

Эндпоинты:
- POST /boards      — создать доску (с колонками To Do / In Progress / Done)
- GET  /boards/{id} — доска с колонками и задачами
- POST /tasks       — создать задачу
- GET  /tasks/{id}  — получить задачу
- PUT  /tasks/{id}  — обновить задачу (перемещение, назначение, поля)

Документация API: Swagger UI — /docs, ReDoc — /redoc.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
import models  # noqa: F401 — регистрируем модели до create_all
from routers import boards_router, tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создание таблиц при старте."""
    await init_db()
    yield


app = FastAPI(
    title="Kanban Service",
    description=(
        "Управление досками и задачами: создание доски при создании проекта, "
        "колонки To Do / In Progress / Done, задачи, перемещение, назначение исполнителя."
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

app.include_router(boards_router.router)
app.include_router(tasks_router.router)


@app.get("/health", tags=["Служебные"])
async def health():
    """Проверка доступности сервиса."""
    return {"status": "ok", "service": "kanban"}
