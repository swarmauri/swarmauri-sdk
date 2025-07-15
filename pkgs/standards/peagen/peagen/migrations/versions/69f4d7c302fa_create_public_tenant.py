"""create public tenant and default user

Revision ID: 69f4d7c302fa
Revises: dc70c8bef823
Create Date: 2025-07-01 00:00:00
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence, Union

from sqlalchemy import text

revision: str = "69f4d7c302fa"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ───────────────────────── helpers ──────────────────────────
# Use CURRENT_TIMESTAMP for compatibility across different databases
UTC_NOW = text("CURRENT_TIMESTAMP")


def utc_now_naive() -> datetime:
    """Return the current UTC time without tzinfo."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ───────────────────────── migration ─────────────────────────
def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
