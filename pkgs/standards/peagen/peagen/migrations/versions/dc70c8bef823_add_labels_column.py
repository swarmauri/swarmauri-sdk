"""add labels column to tasks

Revision ID: dc70c8bef823
Revises:
Create Date: 2025-06-30 05:20:00
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "dc70c8bef823"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add labels column to tasks."""
    op.add_column(
        "tasks",
        sa.Column(
            "labels",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )


def downgrade() -> None:
    """Remove labels column from tasks."""
    op.drop_column("tasks", "labels")
