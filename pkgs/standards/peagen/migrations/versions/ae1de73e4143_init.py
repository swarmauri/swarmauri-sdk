# alembic revision: ae1de73e4143_init.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from peagen.models.task_run import status_enum      # ← shared object, create_type=False

revision = "ae1de73e4143"
down_revision = None

def _table_missing(bind, name: str) -> bool:
    return name not in inspect(bind).get_table_names()

def upgrade() -> None:
    bind = op.get_bind()

    # 1) ensure enum exists (idempotent)
    status_enum.create(bind, checkfirst=True)

    # 2) create table only if it doesn't exist
    if _table_missing(bind, "task_runs"):
        op.create_table(
            "task_runs",
            sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("pool", sa.String()),
            sa.Column("task_type", sa.String()),
            sa.Column("status", status_enum, nullable=False),
            sa.Column("payload", sa.JSON()),
            sa.Column("result", sa.JSON()),
            sa.Column("deps", sa.JSON(), nullable=False),
            sa.Column("edge_pred", sa.String()),
            sa.Column("labels", sa.JSON(), nullable=False),
            sa.Column("groups", sa.JSON(), nullable=False),
            sa.Column("config_toml", sa.String()),
            sa.Column("artifact_uri", sa.String()),
            sa.Column("started_at", sa.TIMESTAMP(timezone=True)),
            sa.Column("finished_at", sa.TIMESTAMP(timezone=True)),
        )
    # else: table already present → skip and preserve rows

def downgrade() -> None:
    bind = op.get_bind()
    if not _table_missing(bind, "task_runs"):
        op.drop_table("task_runs")
