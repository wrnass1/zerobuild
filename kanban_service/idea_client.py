from __future__ import annotations

"""Запросы к Idea Service (каталог идей)."""
import httpx

from config import settings


class IdeaServiceError(Exception):
    """Idea Service недоступен или ответил ошибкой."""


async def fetch_idea(idea_id: int) -> dict | None:
    """GET /ideas/{id}. None если 404."""
    base = settings.idea_service_url.rstrip("/")
    url = f"{base}/ideas/{idea_id}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url)
    except httpx.RequestError as e:
        raise IdeaServiceError(str(e)) from e
    if resp.status_code == 404:
        return None
    if resp.status_code != 200:
        raise IdeaServiceError(f"HTTP {resp.status_code}")
    return resp.json()
