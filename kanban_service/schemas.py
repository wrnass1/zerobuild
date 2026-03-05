"""Pydantic-схемы для Kanban Service."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BoardCreate(BaseModel):
    """Создание доски."""

    name: str = Field(..., description="Название доски")
    project_id: Optional[int] = Field(None, description="ID проекта")
    idea_id: Optional[int] = Field(None, description="ID идеи")


class ColumnResponse(BaseModel):
    """Колонка в ответе."""

    id: int
    board_id: int
    name: str
    position: int

    model_config = {"from_attributes": True}


class TaskBrief(BaseModel):
    """Краткое представление задачи."""

    id: int
    board_id: int
    column_id: int
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    deadline: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ColumnWithTasks(ColumnResponse):
    """Колонка с задачами."""

    tasks: List[TaskBrief] = []


class BoardResponse(BaseModel):
    """Доска в ответе."""

    id: int
    name: str
    project_id: Optional[int] = None
    idea_id: Optional[int] = None

    model_config = {"from_attributes": True}


class BoardDetailResponse(BoardResponse):
    """Доска с колонками и задачами."""

    columns: List[ColumnWithTasks] = []


class TaskCreate(BaseModel):
    """Создание задачи."""

    board_id: int = Field(..., description="ID доски")
    column_id: int = Field(..., description="ID колонки")
    title: str = Field(..., description="Название задачи")
    description: Optional[str] = Field(None, description="Описание")
    assignee_id: Optional[int] = Field(None, description="ID исполнителя")
    deadline: Optional[datetime] = Field(None, description="Дедлайн")


class TaskUpdate(BaseModel):
    """Обновление задачи (перемещение, назначение, поля)."""

    column_id: Optional[int] = Field(None, description="ID колонки (перемещение)")
    title: Optional[str] = Field(None, description="Название")
    description: Optional[str] = Field(None, description="Описание")
    assignee_id: Optional[int] = Field(None, description="ID исполнителя")
    deadline: Optional[datetime] = Field(None, description="Дедлайн")


class TaskResponse(BaseModel):
    """Задача в ответе."""

    id: int
    board_id: int
    column_id: int
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    deadline: Optional[datetime] = None

    model_config = {"from_attributes": True}
