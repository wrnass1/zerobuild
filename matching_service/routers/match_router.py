"""Эндпоинт подбора кандидатов для идеи (stateless, без БД)."""
from typing import List

import httpx
from fastapi import APIRouter, HTTPException, Query, status

from config import settings
from schemas import MatchResponse, MatchItem

router = APIRouter(prefix="", tags=["Matching"])


async def _fetch_idea(idea_id: int) -> dict:
    """Получить идею из Idea Service."""
    url = f"{settings.ideas_url.rstrip('/')}/ideas/{idea_id}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Idea Service недоступен: {exc}",
            ) from exc
    if resp.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Идея не найдена",
        )
    if resp.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка Idea Service: {resp.status_code}",
        )
    return resp.json()


async def _fetch_candidates() -> List[dict]:
    """Получить список кандидатов из Auth Service.

    В качестве кандидатов рассматриваются все пользователи (их профили).
    Ожидается эндпоинт Auth Service: GET /profiles (список профилей).
    """
    url = f"{settings.auth_url.rstrip('/')}/profiles"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Auth Service недоступен: {exc}",
            ) from exc
    if resp.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка Auth Service: {resp.status_code}",
        )
    data = resp.json()
    if not isinstance(data, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Auth Service вернул неожиданный формат профилей",
        )
    return data


def _calc_match_score(
    required_stack: List[str],
    tech_stack: List[str],
    idea_complexity: str | None,
    user_level: str | None,
    user_projects_count: int,
) -> tuple[int, List[str], List[str]]:
    """Расширенный алгоритм совпадения стека/уровня.

    Базовый принцип:
    - 0–80%: процент пересечения стеков;
    - до +15%: соответствие уровня пользователя сложности идеи;
    - до -10%: штраф за сильную загруженность (много проектов).
    """
    required = [t.lower() for t in required_stack]
    candidate = [t.lower() for t in tech_stack]
    if not required:
        return 0, [], []

    overlap = sorted({t for t in candidate if t in required})
    missing = sorted({t for t in required if t not in candidate})

    base_score = int(80 * len(overlap) / len(required))

    # Соответствие уровня сложности
    level_bonus = 0
    if user_level and idea_complexity:
        lvl = user_level.lower()
        cmpx = idea_complexity.lower()
        if cmpx == "low":
            # Подойдут и junior, и middle
            level_bonus = 10
        elif cmpx == "medium":
            level_bonus = 15 if lvl == "middle" else 5
        elif cmpx == "high":
            level_bonus = 15 if lvl == "middle" else 0

    # Штраф за высокую загруженность (много проектов)
    busy_penalty = 0
    if user_projects_count >= 3:
        busy_penalty = 10
    elif user_projects_count == 2:
        busy_penalty = 5

    score = max(0, min(100, base_score + level_bonus - busy_penalty))
    return score, overlap, missing


@router.get(
    "/match/{idea_id}",
    response_model=MatchResponse,
    summary="Подбор кандидатов для идеи",
    description=(
        "Stateless-подбор кандидатов: идея берётся из Idea Service, кандидаты — из Auth Service. "
        "Результат отсортирован по коэффициенту совпадения стека и уровня."
    ),
)
async def match_candidates_for_idea(
    idea_id: int,
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество кандидатов в ответе"),
):
    """Подбор кандидатов по стеку и уровню сложности идеи."""
    idea = await _fetch_idea(idea_id)
    candidates = await _fetch_candidates()

    required_stack: List[str] = idea.get("required_stack") or []
    idea_complexity = idea.get("complexity")

    scored: List[MatchItem] = []
    for profile in candidates:
        tech_stack = profile.get("tech_stack") or []
        level = profile.get("level")
        projects = profile.get("projects") or []

        score, overlap, missing = _calc_match_score(
            required_stack,
            tech_stack,
            idea_complexity,
            level,
            len(projects),
        )
        if score == 0:
            continue
        scored.append(
            MatchItem(
                candidate_id=profile["id"],
                user_id=profile["id"],
                name=profile.get("name"),
                level=level,  # type: ignore[arg-type]
                score=score,
                overlap_stack=overlap,
                missing_stack=missing,
            )
        )

    scored.sort(key=lambda x: x.score, reverse=True)
    return MatchResponse(idea_id=idea["id"], matches=scored[:limit])


