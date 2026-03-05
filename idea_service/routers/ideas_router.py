"""Эндпоинты CRUD для идей."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Idea, IdeaStatus, ComplexityLevel
from schemas import IdeaCreate, IdeaUpdate, IdeaResponse, IdeaStatusEnum, ComplexityLevelEnum

router = APIRouter(prefix="/ideas", tags=["Ideas"])


@router.get(
    "",
    response_model=List[IdeaResponse],
    summary="Список идей",
    description="Каталог идей с фильтрацией по стеку, сложности и поиску по названию.",
)
@router.get(
    "/list",
    response_model=List[IdeaResponse],
    summary="Список идей (alias)",
    include_in_schema=True,
)
async def list_ideas(
    search: Optional[str] = Query(None, description="Поиск по названию (подстрока)"),
    stack: Optional[str] = Query(None, description="Фильтр по технологии в стеке"),
    complexity: Optional[ComplexityLevelEnum] = Query(None, description="Фильтр по сложности"),
    status_filter: Optional[IdeaStatusEnum] = Query(None, alias="status", description="Фильтр по статусу"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Список идей с фильтрами."""
    q = select(Idea)
    if search:
        q = q.where(Idea.title.ilike(f"%{search}%"))
    if stack:
        q = q.where(Idea.required_stack.contains([stack]))
    if complexity is not None:
        q = q.where(Idea.complexity == complexity)
    if status_filter is not None:
        q = q.where(Idea.status == status_filter)
    q = q.order_by(Idea.id).offset(offset).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


@router.post(
    "",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать идею",
)
@router.post(
    "/create",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать идею (alias)",
    include_in_schema=True,
)
async def create_idea(
    body: IdeaCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создание новой идеи."""
    idea = Idea(
        title=body.title,
        description=body.description,
        required_stack=body.required_stack,
        complexity=ComplexityLevel(body.complexity.value) if body.complexity else None,
        participants_count=body.participants_count,
        status=IdeaStatus(body.status.value),
    )
    db.add(idea)
    await db.flush()
    await db.refresh(idea)
    return idea


@router.get(
    "/{idea_id}",
    response_model=IdeaResponse,
    summary="Получить идею по ID",
)
@router.get(
    "/get/{idea_id}",
    response_model=IdeaResponse,
    summary="Получить идею по ID (alias)",
    include_in_schema=True,
)
async def get_idea(
    idea_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получение одной идеи."""
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Идея не найдена",
        )
    return idea


@router.put(
    "/{idea_id}",
    response_model=IdeaResponse,
    summary="Обновить идею",
)
@router.put(
    "/update/{idea_id}",
    response_model=IdeaResponse,
    summary="Обновить идею (alias)",
    include_in_schema=True,
)
async def update_idea(
    idea_id: int,
    body: IdeaUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновление идеи (частичное)."""
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Идея не найдена",
        )
    data = body.model_dump(exclude_unset=True)
    if "status" in data and data["status"] is not None:
        data["status"] = IdeaStatus(data["status"].value)
    if "complexity" in data and data["complexity"] is not None:
        data["complexity"] = ComplexityLevel(data["complexity"].value)
    for key, value in data.items():
        setattr(idea, key, value)
    await db.flush()
    await db.refresh(idea)
    return idea


@router.delete(
    "/{idea_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить идею",
)
@router.delete(
    "/delete/{idea_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить идею (alias)",
    include_in_schema=True,
)
async def delete_idea(
    idea_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удаление идеи."""
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Идея не найдена",
        )
    await db.delete(idea)
    return None
