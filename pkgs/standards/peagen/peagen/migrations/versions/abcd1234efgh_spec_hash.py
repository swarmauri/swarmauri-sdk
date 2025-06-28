"""add spec_hash column and unique index"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import json
import hashlib

revision = "abcd1234efgh"
down_revision = "f86f5297311a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("spec_hash", sa.String(length=64), nullable=True),
    )
    bind = op.get_bind()
    rows = list(bind.execute(text("SELECT id, parameters FROM tasks")))
    for row in rows:
        params = row.parameters or {}
        blob = json.dumps(params, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256(blob.encode()).hexdigest()
        bind.execute(
            text("UPDATE tasks SET spec_hash=:h WHERE id=:id"),
            {"h": h, "id": row.id},
        )
    op.alter_column("tasks", "spec_hash", nullable=False)
    op.create_unique_constraint(
        "uq_tasks_tenant_spec_hash",
        "tasks",
        ["tenant_id", "spec_hash"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_tasks_tenant_spec_hash", "tasks", type_="unique")
    op.drop_column("tasks", "spec_hash")
