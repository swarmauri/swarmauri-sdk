from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "e5cf4f2a1b2c"
down_revision = "8c6e6abe8f9d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("task_runs")}
    if "in_degree" not in cols:
        op.add_column(
            "task_runs",
            sa.Column("in_degree", sa.Integer(), nullable=False, server_default="0"),
        )
        op.alter_column("task_runs", "in_degree", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("task_runs")}
    if "in_degree" in cols:
        op.drop_column("task_runs", "in_degree")
