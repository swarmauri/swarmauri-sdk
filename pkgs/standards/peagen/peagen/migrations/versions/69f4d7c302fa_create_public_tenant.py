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
from sqlalchemy import text
from alembic import op

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
            sa.column("email", sa.String),
            sa.column("created_at", sa.DateTime(timezone=False)),
            sa.column("updated_at", sa.DateTime(timezone=False)),
        )
        op.bulk_insert(
            tenants,
            [
                {
                    "id": tenant_id,
                    "slug": "public",
                    "name": "Public",
                    "email": "support@swarmauri.com",
                    "created_at": now,
                    "updated_at": now,
                }
            ],
        )

    # ---------- default user ----------
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    if (
        bind.execute(
            sa.text("SELECT 1 FROM users WHERE id = :id"), {"id": str(user_id)}
        ).fetchone()
        is None
    ):
        users = sa.table(
            "users",
            sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("email", sa.String),
            sa.column("tenant_id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("created_at", sa.DateTime(timezone=False)),
            sa.column("updated_at", sa.DateTime(timezone=False)),
        )
        assoc = sa.table(
            "user_tenants",
            sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("tenant_id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("user_id", sa.dialects.postgresql.UUID(as_uuid=True)),
            sa.column("joined_at", sa.DateTime(timezone=False)),
        )

        op.bulk_insert(
            users,
            [
                {
                    "id": user_id,
                    "email": "public@example.com",
                    "tenant_id": tenant_id,
                    "created_at": now,
                    "updated_at": now,
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
                    "joined_at": now,
                }
            ],
        )

    # ---------- default pool ----------
    pool_id = uuid.UUID(int=0)
    if (
        bind.execute(
            sa.text("SELECT 1 FROM pools WHERE id = :id"), {"id": str(pool_id)}
        ).fetchone()
        is None
    ):
        op.bulk_insert(
            pools,
            [
                {
                    "id": pool_id,
                    "tenant_id": tenant_id,
                    "name": "default",
                    "created_at": now,
                    "updated_at": now,
                }
            ],
        )


def downgrade() -> None:
    """Intentionally left empty; keep the public tenant and user."""
    pass
