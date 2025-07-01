"""create public tenant

Revision ID: 69f4d7c302fa
Revises: dc70c8bef823
Create Date: 2025-07-01 00:00:00
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "69f4d7c302fa"
down_revision: Union[str, None] = "dc70c8bef823"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create a public tenant if it does not exist."""
    bind = op.get_bind()
    result = bind.execute(
        sa.text("SELECT id FROM tenants WHERE slug=:slug"), {"slug": "public"}
    )
    if result.fetchone() is None:
        tenants = sa.table(
            "tenants",
            sa.column("id", sa.String),
            sa.column("slug", sa.String),
            sa.column("name", sa.String),
            sa.column("date_created", sa.DateTime),
            sa.column("last_modified", sa.DateTime),
        )
        now = datetime.now(timezone.utc)
        op.bulk_insert(
            tenants,
            [
                {
                    "id": str(uuid.uuid4()),
                    "slug": "public",
                    "name": "Public",
                    "date_created": now,
                    "last_modified": now,
                }
            ],
        )


def downgrade() -> None:
    """No-op downgrade."""
    pass
