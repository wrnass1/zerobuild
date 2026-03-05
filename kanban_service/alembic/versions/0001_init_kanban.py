"""Initial schema for Kanban Service.

Creates tables `boards`, `board_columns`, `tasks` based on SQLAlchemy models.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_init_kanban"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "boards",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("idea_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_boards_id",
        "boards",
        ["id"],
        unique=False,
    )

    op.create_table(
        "board_columns",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("board_id", sa.Integer(), sa.ForeignKey("boards.id"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "position",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_index(
        "ix_board_columns_id",
        "board_columns",
        ["id"],
        unique=False,
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("board_id", sa.Integer(), sa.ForeignKey("boards.id"), nullable=False),
        sa.Column(
            "column_id",
            sa.Integer(),
            sa.ForeignKey("board_columns.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("assignee_id", sa.Integer(), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_tasks_id",
        "tasks",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_tasks_id", table_name="tasks")
    op.drop_table("tasks")

    op.drop_index("ix_board_columns_id", table_name="board_columns")
    op.drop_table("board_columns")

    op.drop_index("ix_boards_id", table_name="boards")
    op.drop_table("boards")

