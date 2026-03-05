"""Initial schema for Idea Service.

Creates table `ideas` based on SQLAlchemy models.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_init_ideas"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    idea_status = sa.Enum(
        "open",
        "in_progress",
        "done",
        name="ideastatus",
    )
    complexity_level = sa.Enum(
        "low",
        "medium",
        "high",
        name="complexitylevel",
    )

    idea_status.create(op.get_bind(), checkfirst=True)
    complexity_level.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "ideas",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "required_stack",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("complexity", complexity_level, nullable=True),
        sa.Column(
            "participants_count",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "status",
            idea_status,
            nullable=False,
            server_default="open",
        ),
    )
    op.create_index(
        "ix_ideas_id",
        "ideas",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_ideas_title",
        "ideas",
        ["title"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_ideas_title", table_name="ideas")
    op.drop_index("ix_ideas_id", table_name="ideas")
    op.drop_table("ideas")

    bind = op.get_bind()
    complexity_level = sa.Enum(
        "low",
        "medium",
        "high",
        name="complexitylevel",
    )
    idea_status = sa.Enum(
        "open",
        "in_progress",
        "done",
        name="ideastatus",
    )
    complexity_level.drop(bind, checkfirst=True)
    idea_status.drop(bind, checkfirst=True)

