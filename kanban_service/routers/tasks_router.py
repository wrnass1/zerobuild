"""Эндпоинты задач."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Task, BoardColumn
from schemas import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать задачу",
)
@router.post(
    "/create",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать задачу (alias)",
    include_in_schema=True,
)
async def create_task(
    body: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создание задачи в указанной колонке доски."""
    col_result = await db.execute(
        select(BoardColumn).where(
            BoardColumn.id == body.column_id,
            BoardColumn.board_id == body.board_id,
        )
    )
    if not col_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Колонка не найдена или не принадлежит доске",
        )
    task = Task(
        board_id=body.board_id,
        column_id=body.column_id,
        title=body.title,
        description=body.description,
        assignee_id=body.assignee_id,
        deadline=body.deadline,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Обновить задачу",
    description="Обновление задачи: перемещение между колонками, назначение исполнителя, поля.",
)
@router.put(
    "/update/{task_id}",
    response_model=TaskResponse,
    summary="Обновить задачу (alias)",
    include_in_schema=True,
)
async def update_task(
    task_id: int,
    body: TaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновление задачи (колонка, исполнитель, название, описание, дедлайн)."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    data = body.model_dump(exclude_unset=True)
    if "column_id" in data and data["column_id"] is not None:
        col_result = await db.execute(
            select(BoardColumn).where(
                BoardColumn.id == data["column_id"],
                BoardColumn.board_id == task.board_id,
            )
        )
        if not col_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Колонка не принадлежит этой доске",
            )
    for key, value in data.items():
        setattr(task, key, value)
    await db.flush()
    await db.refresh(task)
    return task


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Получить задачу по ID",
)
@router.get(
    "/get/{task_id}",
    response_model=TaskResponse,
    summary="Получить задачу по ID (alias)",
    include_in_schema=True,
)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получение одной задачи."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    return task
