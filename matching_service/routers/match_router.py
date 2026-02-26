"""Эндпоинт подбора кандидатов для идеи."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Idea, Candidate
from schemas import MatchResponse, MatchItem

router = APIRouter(prefix="", tags=["Matching"])


def _calc_match_score(required_stack: List[str], tech_stack: List[str]) -> tuple[int, List[str], List[str]]:
    """MVP-алгоритм: процент совпадения требуемого стека и стека кандидата."""
    required = [t.lower() for t in required_stack]
    candidate = [t.lower() for t in tech_stack]
    if not required:
        return 0, [], []
    overlap = sorted({t for t in candidate if t in required})
    missing = sorted({t for t in required if t not in candidate})
    score = int(100 * len(overlap) / len(required))
    return score, overlap, missing


@router.get(
    "/match/{idea_id}",
    response_model=MatchResponse,
    summary="Подбор кандидатов для идеи",
    description="Возвращает список кандидатов, отсортированный по проценту совпадения стека.",
)
async def match_candidates_for_idea(
    idea_id: int,
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество кандидатов в ответе"),
    db: AsyncSession = Depends(get_db),
):
    """Подбор кандидатов по стеку для указанной идеи."""
    idea_result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = idea_result.scalar_one_or_none()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Идея не найдена",
        )

    candidates_result = await db.execute(select(Candidate))
    candidates = candidates_result.scalars().all()

    scored: List[MatchItem] = []
    for candidate in candidates:
        score, overlap, missing = _calc_match_score(idea.required_stack or [], candidate.tech_stack or [])
        if score == 0:
            continue
        scored.append(
            MatchItem(
                candidate_id=candidate.id,
                user_id=candidate.user_id,
                name=candidate.name,
                level=candidate.level,  # type: ignore[arg-type]
                score=score,
                overlap_stack=overlap,
                missing_stack=missing,
            )
        )

    scored.sort(key=lambda x: x.score, reverse=True)
    return MatchResponse(idea_id=idea.id, matches=scored[:limit])

