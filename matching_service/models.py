"""Модели БД для Matching Service."""
import enum
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from database import Base


class UserLevel(str, enum.Enum):
    """Уровень пользователя."""

    JUNIOR = "junior"
    MIDDLE = "middle"


class Idea(Base):
    """Идея проекта (минимальный срез для матчинга)."""

    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    required_stack = Column(ARRAY(String), nullable=False, default=list)


class Candidate(Base):
    """Кандидат (снимок пользователя для матчинга)."""

    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    level = Column(Enum(UserLevel), nullable=True)
    tech_stack = Column(ARRAY(String), nullable=False, default=list)
    description = Column(Text, nullable=True)


class InviteStatus(str, enum.Enum):
    """Статус приглашения в проект."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Invite(Base):
    """Приглашение кандидата в идею/проект."""

    __tablename__ = "invites"

    id = Column(Integer, primary_key=True, index=True)
    # ID идеи в Idea Service (каталог), не FK на локальную таблицу ideas
    idea_id = Column(Integer, nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    status = Column(Enum(InviteStatus), nullable=False, default=InviteStatus.PENDING)

    candidate = relationship("Candidate")

