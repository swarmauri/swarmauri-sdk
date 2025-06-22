from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "f2a4b3c5d6e7"
down_revision = "e5cf4f2a1b2c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("task_runs")}
    if "config_toml" not in cols:
        op.add_column("task_runs", sa.Column("config_toml", sa.String()))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("task_runs")}
    if "config_toml" in cols:
        op.drop_column("task_runs", "config_toml")
