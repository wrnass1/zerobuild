"""Модели БД для Kanban Service."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base


class Board(Base):
    """Доска (проект)."""

    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    project_id = Column(Integer, nullable=True, index=True)
    idea_id = Column(Integer, nullable=True, index=True)

    columns = relationship("BoardColumn", back_populates="board", order_by="BoardColumn.position")
    tasks = relationship("Task", back_populates="board")


class BoardColumn(Base):
    """Колонка на доске (To Do, In Progress, Done)."""

    __tablename__ = "board_columns"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    name = Column(String(100), nullable=False)
    position = Column(Integer, nullable=False, default=0)

    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column")


class Task(Base):
    """Задача на доске."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    column_id = Column(Integer, ForeignKey("board_columns.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assignee_id = Column(Integer, nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)

    board = relationship("Board", back_populates="tasks")
    column = relationship("BoardColumn", back_populates="tasks")
