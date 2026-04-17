"""Эндпоинты досок."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth_deps import get_current_user_id
from board_access import require_board_access
from database import get_db
from idea_client import IdeaServiceError, fetch_idea
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
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Создание доски с колонками по умолчанию."""
    if body.idea_id is not None:
        try:
            idea = await fetch_idea(body.idea_id)
        except IdeaServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Idea Service: {e!s}",
            ) from e
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Идея не найдена в каталоге",
            )
        owner = idea.get("owner_id")
        if owner is not None and owner != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Привязать к доске можно только свою идею",
            )
    board = Board(
        owner_id=user_id,
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
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Получение доски с колонками и задачами."""
    await require_board_access(db, board_id, user_id)
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
        owner_id=board.owner_id,
        name=board.name,
        project_id=board.project_id,
        idea_id=board.idea_id,
        columns=columns_data,
    )
