"""Эндпоинты досок."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Board, BoardColumn
from schemas import BoardCreate, BoardResponse, BoardDetailResponse, ColumnWithTasks, TaskBrief

router = APIRouter(prefix="/boards", tags=["Boards"])

DEFAULT_COLUMNS = ["To Do", "In Progress", "Done"]


@router.post(
    "",
    response_model=BoardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать доску",
    description="Создаёт доску и колонки по умолчанию: To Do, In Progress, Done.",
)
@router.post(
    "/create",
    response_model=BoardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать доску (alias)",
    include_in_schema=True,
)
async def create_board(
    body: BoardCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создание доски с колонками по умолчанию."""
    board = Board(
        name=body.name,
        project_id=body.project_id,
        idea_id=body.idea_id,
    )
    db.add(board)
    await db.flush()
    for i, name in enumerate(DEFAULT_COLUMNS):
        col = BoardColumn(board_id=board.id, name=name, position=i)
        db.add(col)
    await db.flush()
    await db.refresh(board)
    return board


@router.get(
    "/{board_id}",
    response_model=BoardDetailResponse,
    summary="Получить доску с колонками и задачами",
)
@router.get(
    "/get/{board_id}",
    response_model=BoardDetailResponse,
    summary="Получить доску (alias)",
    include_in_schema=True,
)
async def get_board(
    board_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получение доски с колонками и задачами."""
    result = await db.execute(
        select(Board)
        .where(Board.id == board_id)
        .options(
            selectinload(Board.columns).selectinload(BoardColumn.tasks),
        )
    )
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доска не найдена",
        )
    columns_data = [
        ColumnWithTasks(
            id=c.id,
            board_id=c.board_id,
            name=c.name,
            position=c.position,
            tasks=[TaskBrief.model_validate(t) for t in c.tasks],
        )
        for c in sorted(board.columns, key=lambda x: x.position)
    ]
    return BoardDetailResponse(
        id=board.id,
        name=board.name,
        project_id=board.project_id,
        idea_id=board.idea_id,
        columns=columns_data,
    )
