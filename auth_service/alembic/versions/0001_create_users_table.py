"""Create users table

Revision ID: 0001_create_users_table
Revises:
Create Date: 2026-03-03 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_create_users_table"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column(
            "level",
            sa.Enum("junior", "middle", name="userlevel", create_type=False),
            nullable=True,
        ),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("tech_stack", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("projects", postgresql.JSONB, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("users")

