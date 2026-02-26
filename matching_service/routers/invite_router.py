"""Эндпоинты управления идеями, кандидатами и приглашениями."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Idea, Candidate, Invite, InviteStatus
from schemas import (
    IdeaCreate,
    IdeaResponse,
    CandidateCreate,
    CandidateResponse,
    InviteCreate,
    InviteResponse,
)

router = APIRouter(prefix="", tags=["Ideas & Invites"])


@router.post(
    "/ideas",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать идею для матчинга",
)
async def create_idea(
    body: IdeaCreate,
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
    db: AsyncSession = Depends(get_db),
):
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
    db: AsyncSession = Depends(get_db),
):
    idea_result = await db.execute(select(Idea).where(Idea.id == body.idea_id))
    idea = idea_result.scalar_one_or_none()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Идея не найдена",
        )

    candidate_result = await db.execute(select(Candidate).where(Candidate.id == body.candidate_id))
    candidate = candidate_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кандидат не найден",
        )

    invite = Invite(
        idea_id=idea.id,
        candidate_id=candidate.id,
        status=InviteStatus.PENDING,
    )
    db.add(invite)
    await db.flush()
    return InviteResponse.model_validate(invite)

