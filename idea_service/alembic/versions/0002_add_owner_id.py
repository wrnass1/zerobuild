"""Add owner_id to ideas table.

This aligns DB schema with SQLAlchemy model `Idea.owner_id`.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_add_owner_id"
down_revision: Union[str, None] = "0001_init_ideas"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ideas", sa.Column("owner_id", sa.Integer(), nullable=True))
    op.create_index("ix_ideas_owner_id", "ideas", ["owner_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ideas_owner_id", table_name="ideas")
    op.drop_column("ideas", "owner_id")

