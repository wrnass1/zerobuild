"""Pydantic-схемы для Idea Service."""
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class IdeaStatusEnum(str, Enum):
    """Статус идеи."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class ComplexityLevelEnum(str, Enum):
    """Уровень сложности."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IdeaCreate(BaseModel):
    """Создание идеи."""

    title: str = Field(..., description="Название идеи")
    description: Optional[str] = Field(None, description="Описание")
    required_stack: List[str] = Field(default_factory=list, description="Предполагаемый стек")
    complexity: Optional[ComplexityLevelEnum] = Field(None, description="Уровень сложности")
    participants_count: int = Field(1, ge=1, description="Количество участников")
    status: IdeaStatusEnum = Field(IdeaStatusEnum.OPEN, description="Статус")


class IdeaUpdate(BaseModel):
    """Обновление идеи (все поля опциональны)."""

    title: Optional[str] = Field(None, description="Название идеи")
    description: Optional[str] = Field(None, description="Описание")
    required_stack: Optional[List[str]] = Field(None, description="Предполагаемый стек")
    complexity: Optional[ComplexityLevelEnum] = Field(None, description="Уровень сложности")
    participants_count: Optional[int] = Field(None, ge=1, description="Количество участников")
    status: Optional[IdeaStatusEnum] = Field(None, description="Статус")


class IdeaResponse(BaseModel):
    """Идея в ответе."""

    id: int
    owner_id: Optional[int] = Field(None, description="ID владельца (Auth Service)")
    title: str
    description: Optional[str] = None
    required_stack: List[str]
    complexity: Optional[ComplexityLevelEnum] = None
    participants_count: int
    status: IdeaStatusEnum

    model_config = {"from_attributes": True}
