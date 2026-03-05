"""
API Gateway — единая точка входа.

Маршрутизация:
- /api/auth   -> auth-service:8000
- /api/ideas  -> idea-service:8002
- /api/kanban -> kanban-service:8003
- /api/match  -> matching-service:8001
"""
import asyncio
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response

from config import settings
from openapi_merge import SERVICE_PREFIXES, fetch_openapi, merge_specs

# Кэш объединённой OpenAPI (заполняется при старте)
_merged_openapi: dict | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """При старте загружаем OpenAPI со всех сервисов и объединяем для Swagger."""
    global _merged_openapi
    # Даём сервисам (в т.ч. auth) время подняться после depends_on
    await asyncio.sleep(5)
    urls = [
        settings.auth_url,
        settings.ideas_url,
        settings.kanban_url,
        settings.matching_url,
    ]
    async with httpx.AsyncClient() as client:
        specs = []
        for (_, merge_path_prefix, schema_prefix), base_url in zip(SERVICE_PREFIXES, urls):
            spec = await fetch_openapi(client, base_url)
            specs.append((spec, merge_path_prefix, schema_prefix))
        _merged_openapi = merge_specs(specs)
    yield


def custom_openapi():
    """Возвращает объединённую OpenAPI — все эндпоинты в одном Swagger."""
    if _merged_openapi is not None:
        return _merged_openapi
    return {
        "openapi": "3.1.0",
        "info": {"title": "API Gateway", "version": "1.0.0"},
        "paths": {},
        "components": {"schemas": {}},
    }


app = FastAPI(
    title="API Gateway",
    description="Единая точка входа к сервисам платформы pet-проектов.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
app.openapi = custom_openapi

# Префиксы и базовые URL сервисов
ROUTES = [
    ("/api/auth", settings.auth_url, lambda p: p[len("/api/auth"):] or "/"),
    ("/api/ideas", settings.ideas_url, lambda p: "/ideas" + (p[len("/api/ideas"):] or "")),
    ("/api/kanban", settings.kanban_url, lambda p: p[len("/api/kanban"):] or "/"),
    ("/api/match", settings.matching_url, lambda p: p[len("/api/match"):] or "/"),
]


def get_upstream(path: str) -> tuple[str, str] | None:
    """Возвращает (base_url, target_path) для запроса или None."""
    for prefix, base_url, path_fn in ROUTES:
        if path == prefix or path.startswith(prefix + "/"):
            target_path = path_fn(path)
            return base_url.rstrip("/"), target_path or "/"
    return None


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
async def proxy(request: Request, path: str):
    """Проксирование запроса к соответствующему сервису."""
    full_path = f"/api/{path}" if path else "/api"
    upstream = get_upstream(full_path)
    if not upstream:
        return Response(content="Not Found", status_code=404)
    base_url, target_path = upstream
    url = f"{base_url}{target_path}"
    if request.url.query:
        url += f"?{request.url.query}"
    forward_headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    body = await request.body()
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                request.method,
                url,
                content=body,
                headers=forward_headers,
                timeout=30.0,
            )
        except httpx.RequestError as e:
            return Response(
                content=f"Upstream error: {e!s}",
                status_code=502,
            )
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers={k: v for k, v in resp.headers.items() if k.lower() not in ("transfer-encoding", "connection")},
    )


@app.get("/health", tags=["Служебные"])
async def health():
    """Проверка доступности gateway."""
    return {"status": "ok", "service": "gateway"}


@app.post("/openapi/refresh", tags=["Служебные"])
async def refresh_openapi():
    """Перезагрузить OpenAPI со всех сервисов (если при старте кого-то не было)."""
    global _merged_openapi
    urls = [
        settings.auth_url,
        settings.ideas_url,
        settings.kanban_url,
        settings.matching_url,
    ]
    async with httpx.AsyncClient() as client:
        specs = []
        for (_, merge_path_prefix, schema_prefix), base_url in zip(SERVICE_PREFIXES, urls):
            spec = await fetch_openapi(client, base_url, retries=2, retry_delay=1.0)
            specs.append((spec, merge_path_prefix, schema_prefix))
    _merged_openapi = merge_specs(specs)
    return {"status": "ok", "message": "OpenAPI обновлён, обновите страницу /docs"}
