"""Эндпоинты: регистрация и вход."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from schemas import UserRegister, UserLogin, Token
from auth_jwt import hash_password, verify_password, create_access_token

router = APIRouter(prefix="", tags=["Авторизация"])


@router.post(
    "/register",
    response_model=Token,
    summary="Регистрация пользователя",
    description="Создание нового пользователя. Возвращает JWT для последующей авторизации.",
)
async def register(
    body: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Регистрация: email + пароль + опционально имя. Возвращает JWT."""
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже зарегистрирован",
        )
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        name=body.name,
    )
    db.add(user)
    await db.flush()
    # user.id уже установлен после flush
    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=str(token), token_type="bearer")


@router.post(
    "/login",
    response_model=Token,
    summary="Вход (логин)",
    description="Авторизация по email и паролю. Возвращает JWT.",
)
async def login(
    body: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Вход: проверка пароля и выдача JWT."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )
    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=str(token), token_type="bearer")
