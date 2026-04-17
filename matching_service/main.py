"""
Matching Service — stateless-сервис подбора участников по стеку для идей.

Особенности:
- не хранит собственные данные и не использует БД;
- получает идеи из Idea Service;
- получает кандидатов из Auth Service (профили пользователей);
- рассчитывает коэффициент совпадения и возвращает отсортированный список.

Документация API: Swagger UI — /docs, ReDoc — /redoc.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import match_router, invite_router


app = FastAPI(
    title="Matching Service",
    description=(
        "Сервис подбора участников по стеку технологий. "
        "Stateless: использует Idea Service и Auth Service как источники данных."
    ),
    version="1.0.0",
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

