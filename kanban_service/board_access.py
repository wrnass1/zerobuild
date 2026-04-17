"""Проверка доступа к доске по владельцу (JWT user_id)."""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Board


async def require_board_access(db: AsyncSession, board_id: int, user_id: int) -> Board:
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доска не найдена",
        )
    if board.owner_id is not None and board.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к доске",
        )
    return board
