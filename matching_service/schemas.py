"""Pydantic-схемы для Matching Service."""
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class UserLevelEnum(str, Enum):
    """Уровень пользователя."""

    JUNIOR = "junior"
    MIDDLE = "middle"


class IdeaCreate(BaseModel):
    """Создание идеи (минимальный набор полей для матчинга)."""

    title: str = Field(..., description="Название идеи")
    description: Optional[str] = Field(None, description="Описание идеи")
    required_stack: List[str] = Field(..., description="Требуемый стек технологий")


class IdeaResponse(IdeaCreate):
    """Идея в ответе."""

    id: int

    class Config:
        from_attributes = True


class CandidateCreate(BaseModel):
    """Создание/обновление кандидата."""

    user_id: int = Field(..., description="ID пользователя из Auth Service")
    name: Optional[str] = Field(None, description="Имя кандидата")
    level: Optional[UserLevelEnum] = Field(None, description="Уровень (junior/middle)")
    tech_stack: List[str] = Field(..., description="Стек технологий кандидата")
    description: Optional[str] = Field(None, description="Описание/о себе")


class CandidateResponse(CandidateCreate):
    """Кандидат в ответе."""

    id: int

    class Config:
        from_attributes = True


class MatchItem(BaseModel):
    """Один кандидат в результате матчинга."""

    candidate_id: int = Field(..., description="Совпадает с user_id в Auth Service")
    user_id: int = Field(..., description="ID пользователя из Auth Service")
    name: Optional[str] = Field(None, description="Имя кандидата")
    level: Optional[UserLevelEnum] = Field(None, description="Уровень")
    score: int = Field(..., description="Процент совпадения стеков (0–100)")
    overlap_stack: List[str] = Field(..., description="Совпадающие технологии")
    missing_stack: List[str] = Field(..., description="Технологии из идеи, которых не хватает у кандидата")


class MatchResponse(BaseModel):
    """Результат матчинга для идеи."""

    idea_id: int
    matches: List[MatchItem]


class InviteCreate(BaseModel):
    """Запрос на отправку приглашения."""

    idea_id: int = Field(..., description="ID идеи в Idea Service")
    candidate_id: int = Field(..., description="user_id приглашаемого в Auth Service")


class InviteStatusEnum(str, Enum):
    """Статус приглашения."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class InviteResponse(BaseModel):
    """Информация о приглашении."""

    id: int
    idea_id: int
    candidate_id: int
    status: InviteStatusEnum

    class Config:
        from_attributes = True

