"""Pydantic-схемы для API Auth Service."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class UserLevelEnum(str, Enum):
    """Уровень пользователя (Junior / Middle)."""

    JUNIOR = "junior"
    MIDDLE = "middle"


# ----- Register / Login -----


class UserRegister(BaseModel):
    """Тело запроса регистрации."""

    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, description="Пароль (минимум 6 символов)")
    name: Optional[str] = Field(None, description="Имя")


class UserLogin(BaseModel):
    """Тело запроса входа."""

    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., description="Пароль")


class Token(BaseModel):
    """Ответ с JWT."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Тип токена")


# ----- Profile -----


class ProfileUpdate(BaseModel):
    """Обновление профиля (все поля опциональны)."""

    name: Optional[str] = Field(None, description="Имя")
    level: Optional[UserLevelEnum] = Field(None, description="Уровень: junior / middle")
    description: Optional[str] = Field(None, description="Описание")
    tech_stack: Optional[list[str]] = Field(None, description="Стек технологий")
    projects: Optional[list] = Field(None, description="Список проектов (id)")


class ProfileResponse(BaseModel):
    """Профиль пользователя (ответ)."""

    id: int
    email: str
    name: Optional[str] = None
    level: Optional[str] = None
    description: Optional[str] = None
    tech_stack: list[str] = Field(default_factory=list)
    projects: list = Field(default_factory=list)

    class Config:
        from_attributes = True
