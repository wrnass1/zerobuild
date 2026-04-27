"""Модели БД для Auth Service."""
import enum
from sqlalchemy import Column, Integer, String, Text, Enum, JSON

from database import Base


class UserLevel(str, enum.Enum):
    """Уровень пользователя."""

    JUNIOR = "junior"
    MIDDLE = "middle"


class User(Base):
    """Пользователь."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    level = Column(Enum(UserLevel), nullable=True, default=UserLevel.JUNIOR)
    description = Column(Text, nullable=True)
    # Храним списки в JSON, чтобы модель была совместима с SQLite и Postgres.
    tech_stack = Column(JSON, nullable=True, default=list)
    projects = Column(JSON, nullable=True, default=list)
