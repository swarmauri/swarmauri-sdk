"""create public tenant and default user

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
    """Create a public tenant and a default user if they do not exist."""
    bind = op.get_bind()

    result = bind.execute(
        sa.text("SELECT id FROM tenants WHERE slug=:slug"), {"slug": "public"}
    )
    row = result.fetchone()
    tenant_id = uuid.uuid4() if row is None else row[0]
    if row is None:
        tenants = sa.table(
            "tenants",
            sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
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
                    "id": tenant_id,
                    "slug": "public",
                    "name": "Public",
                    "date_created": now,
                    "last_modified": now,
                }
            ],
        )
    else:
        now = datetime.now(timezone.utc)

    user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    result = bind.execute(
        sa.text("SELECT id FROM users WHERE id=:id"), {"id": str(user_id)}
    )
    if result.fetchone() is None:
        users = sa.table(
            "users",
            sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("username", sa.String),
            sa.column("email", sa.String),
            sa.column("role", sa.String),
            sa.column("date_created", sa.DateTime),
            sa.column("last_modified", sa.DateTime),
        )
        op.bulk_insert(
            users,
            [
                {
                    "id": user_id,
                    "username": "public",
                    "email": "public@example.com",
                    "role": "member",
                    "date_created": now,
                    "last_modified": now,
                }
            ],
        )

        assoc = sa.table(
            "tenant_user_associations",
            sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("tenant_id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("user_id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("role", sa.String),
            sa.column("date_created", sa.DateTime),
            sa.column("last_modified", sa.DateTime),
        )
        op.bulk_insert(
            assoc,
            [
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "role": "owner",
                    "date_created": now,
                    "last_modified": now,
                }
            ],
        )


def downgrade() -> None:
    """No-op downgrade."""
    pass
