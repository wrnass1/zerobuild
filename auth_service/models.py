"""Модели БД для Auth Service."""
import enum
from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

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
    tech_stack = Column(ARRAY(String), nullable=True, default=list)
    projects = Column(JSONB, nullable=True, default=list)
