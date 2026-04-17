"""Эндпоинты управления идеями, кандидатами и приглашениями."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_deps import get_current_user_id
from database import get_db
from idea_client import IdeaServiceError, fetch_idea
from models import Candidate, Invite, InviteStatus
from schemas import (
    IdeaCreate,
    IdeaResponse,
    CandidateCreate,
    CandidateResponse,
    InviteCreate,
    InviteResponse,
)

router = APIRouter(prefix="", tags=["Ideas & Invites"])


def _ensure_inviter_is_idea_owner(idea_payload: dict, user_id: int) -> None:
    owner = idea_payload.get("owner_id")
    if owner is not None and owner != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Приглашать кандидатов может только владелец идеи",
        )


@router.post(
    "/ideas",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать идею для матчинга",
)
async def create_idea(
    body: IdeaCreate,
    _user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    idea = Idea(
        title=body.title,
        description=body.description,
        required_stack=body.required_stack,
    )
    db.add(idea)
    await db.flush()
    return IdeaResponse.model_validate(idea)


@router.post(
    "/candidates",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать кандидата для матчинга",
)
async def create_candidate(
    body: CandidateCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if body.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id в теле запроса должен совпадать с авторизованным пользователем",
        )
    candidate = Candidate(
        user_id=body.user_id,
        name=body.name,
        level=body.level,  # type: ignore[arg-type]
        tech_stack=body.tech_stack,
        description=body.description,
    )
    db.add(candidate)
    await db.flush()
    return CandidateResponse.model_validate(candidate)


@router.post(
    "/invite",
    response_model=InviteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Отправить приглашение кандидату",
    description="Создаёт приглашение кандидату в указанный проект/идею.",
)
async def create_invite(
    body: InviteCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        idea_payload = await fetch_idea(body.idea_id)
    except IdeaServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Idea Service: {e!s}",
        ) from e
    if not idea_payload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Идея не найдена",
        )
    _ensure_inviter_is_idea_owner(idea_payload, user_id)

    candidate_result = await db.execute(select(Candidate).where(Candidate.id == body.candidate_id))
    candidate = candidate_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кандидат не найден",
        )

    invite = Invite(
        idea_id=body.idea_id,
        candidate_id=candidate.id,
        status=InviteStatus.PENDING,
    )
    db.add(invite)
    await db.flush()
    return InviteResponse.model_validate(invite)

