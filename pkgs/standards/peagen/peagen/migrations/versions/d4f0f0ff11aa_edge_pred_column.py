from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "d4f0f0ff11aa"
down_revision = "c1a2b3c4d5e6"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("task_runs")}
    if "edge_pred" not in cols:
        op.add_column("task_runs", sa.Column("edge_pred", sa.String()))
    if "labels" not in cols:
        op.add_column(
            "task_runs",
            sa.Column("labels", sa.JSON(), nullable=False, server_default="[]"),
        )
        op.alter_column("task_runs", "labels", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("task_runs")}
    if "edge_pred" in cols:
        op.drop_column("task_runs", "edge_pred")
    if "labels" in cols:
        op.drop_column("task_runs", "labels")
