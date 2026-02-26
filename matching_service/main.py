"""
Matching Service — подбор участников по стеку для идей.

Основные эндпоинты:
- GET  /match/{idea_id} — вернуть кандидатов с коэффициентом совпадения
- POST /invite         — создать приглашение кандидату в идею

Дополнительно:
- POST /ideas      — завести идею (название + требуемый стек)
- POST /candidates — завести кандидата (user_id + стек)

Документация API: Swagger UI — /docs, ReDoc — /redoc.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
import models  # noqa: F401 — регистрируем модели до create_all
from routers import match_router, invite_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создание таблиц при старте."""
    await init_db()
    yield


app = FastAPI(
    title="Matching Service",
    description=(
        "Сервис подбора участников по стеку технологий. "
        "MVP-алгоритм — процент совпадения требуемого стека идеи и стека кандидата."
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

app.include_router(match_router.router)
app.include_router(invite_router.router)


@app.get("/health", tags=["Служебные"])
async def health():
    """Проверка доступности Matching Service."""
    return {"status": "ok", "service": "matching"}

