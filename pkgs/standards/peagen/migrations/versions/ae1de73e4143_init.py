from alembic import op
import sqlalchemy as sa
from peagen.models.task_run import status_enum      # ← shared object, create_type=False

revision = "ae1de73e4143"
down_revision = None

def upgrade() -> None:
    op.create_table(
        "task_runs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("pool", sa.String()),
        sa.Column("task_type", sa.String()),
        sa.Column("status", status_enum, nullable=False),   # <- no CREATE TYPE
        sa.Column("payload", sa.JSON()),
        sa.Column("result", sa.JSON()),
        sa.Column("deps", sa.JSON(), nullable=False),
        sa.Column("edge_pred", sa.String()),
        sa.Column("labels", sa.JSON(), nullable=False),
        sa.Column("config_toml", sa.String()),
        sa.Column("artifact_uri", sa.String()),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("finished_at", sa.TIMESTAMP(timezone=True)),
    )

def downgrade() -> None:
    op.drop_table("task_runs")