"""Модели БД для Idea Service."""
import enum
from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.dialects.postgresql import ARRAY

from database import Base


class IdeaStatus(str, enum.Enum):
    """Статус идеи."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class ComplexityLevel(str, enum.Enum):
    """Уровень сложности."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Idea(Base):
    """Идея проекта."""

    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    required_stack = Column(ARRAY(String), nullable=False, default=list)
    complexity = Column(Enum(ComplexityLevel), nullable=True)
    participants_count = Column(Integer, nullable=False, default=1)
    status = Column(Enum(IdeaStatus), nullable=False, default=IdeaStatus.OPEN)
