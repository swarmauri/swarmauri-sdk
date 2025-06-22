from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "8c6e6abe8f9d"
down_revision = "d4f0f0ff11aa"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("task_runs")}

    if "labels" not in cols:
        op.add_column(
            "task_runs",
            sa.Column(
                "labels",
                sa.JSON(),                     # or sa.JSONB() if you prefer
                nullable=False,
                server_default=sa.text("'[]'") # postgres needs explicit json literal
            ),
        )
        op.alter_column("task_runs", "labels", server_default=None)

def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "labels" in {c["name"] for c in inspector.get_columns("task_runs")}:
        op.drop_column("task_runs", "labels")
