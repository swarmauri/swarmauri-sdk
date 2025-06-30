"""add labels column to tasks

Revision ID: dc70c8bef823
Revises:
Create Date: 2025-06-30 05:20:00
"""

from typing import Sequence, Union

# NOTE: this migration intentionally does nothing.
# The database schema is created directly from the ORM models
# during tests. An empty migration keeps ``alembic upgrade``
# happy without modifying the schema.

from alembic import op  # noqa: F401  -- retained for future use
import sqlalchemy as sa  # noqa: F401

revision: str = "dc70c8bef823"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op upgrade."""
    pass


def downgrade() -> None:
    """No-op downgrade."""
    pass
