"""Эндпоинты: профиль пользователя."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User, UserLevel
from schemas import ProfileResponse, ProfileUpdate
from auth_jwt import get_current_user_id

router = APIRouter(prefix="", tags=["Профиль"])


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Получить профиль",
    description="Возвращает профиль текущего пользователя (по JWT).",
)
async def get_profile(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Получение профиля авторизованного пользователя."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return ProfileResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        level=user.level.value if user.level else None,
        description=user.description,
        tech_stack=user.tech_stack or [],
        projects=user.projects or [],
    )


@router.put(
    "/profile",
    response_model=ProfileResponse,
    summary="Обновить профиль",
    description="Обновление имени, уровня, описания, стека технологий и списка проектов.",
)
async def update_profile(
    body: ProfileUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Редактирование профиля (только переданные поля)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    data = body.model_dump(exclude_unset=True)
    if "level" in data and data["level"] is not None:
        data["level"] = UserLevel(data["level"].value)
    for key, value in data.items():
        setattr(user, key, value)
    await db.flush()
    await db.refresh(user)
    return ProfileResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        level=user.level.value if user.level else None,
        description=user.description,
        tech_stack=user.tech_stack or [],
        projects=user.projects or [],
    )


@router.delete(
    "/profile",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить аккаунт",
    description="Удаление профиля текущего пользователя (необратимо).",
)
async def delete_profile(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Удаление аккаунта текущего пользователя."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    await db.delete(user)
    await db.flush()
