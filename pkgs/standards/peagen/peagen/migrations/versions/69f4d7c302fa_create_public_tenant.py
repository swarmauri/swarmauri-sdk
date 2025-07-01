"""create public tenant and default user

Revision ID: 69f4d7c302fa
Revises: dc70c8bef823
Create Date: 2025-07-01 00:00:00
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "69f4d7c302fa"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ───────────────────────── helpers ──────────────────────────
UTC_NOW = text("(now() AT TIME ZONE 'UTC')")


# ───────────────────────── migration ─────────────────────────
def upgrade() -> None:
    bind = op.get_bind()
    now = utc_now_naive()

    # ---------- tenant ----------
    row = bind.execute(
        sa.text("SELECT id FROM tenants WHERE slug = :slug"), {"slug": "public"}
    ).fetchone()

    tenant_id = row[0] if row else uuid.uuid4()

    if row is None:
        tenants = sa.table(
            "tenants",
            sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("slug", sa.String),
            sa.column("name", sa.String),
            sa.column("date_created", sa.DateTime(timezone=False)),
            sa.column("last_modified", sa.DateTime(timezone=False)),
        )
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

    # ---------- default user ----------
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    if bind.execute(
        sa.text("SELECT 1 FROM users WHERE id = :id"), {"id": str(user_id)}
    ).fetchone() is None:
        users = sa.table(
            "users",
            sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("username", sa.String),
            sa.column("email", sa.String),
            sa.column("role", sa.String),
            sa.column("date_created", sa.DateTime(timezone=False)),
            sa.column("last_modified", sa.DateTime(timezone=False)),
        )
        assoc = sa.table(
            "tenant_user_associations",
            sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("tenant_id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("user_id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("role", sa.String),
            sa.column("date_created", sa.DateTime(timezone=False)),
            sa.column("last_modified", sa.DateTime(timezone=False)),
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
    """Intentionally left empty; keep the public tenant and user."""
    pass
