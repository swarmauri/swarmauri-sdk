# alembic revision: ae1de73e4143_init.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from peagen.orm.status import Status

status_enum = sa.Enum(
    Status,
    name="task_status_enum",
    create_type=False,
)  # shared object used across revisions

revision = "ae1de73e4143"
down_revision = None


def _table_missing(bind, name: str) -> bool:
    return name not in inspect(bind).get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    # 1) ensure enum exists (idempotent)
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'task_status_enum'
                ) THEN
                    CREATE TYPE task_status_enum AS ENUM (
                        'queued',
                        'waiting',
                        'input_required',
                        'auth_required',
                        'approved',
                        'rejected',
                        'dispatched',
                        'running',
                        'paused',
                        'success',
                        'failed',
                        'cancelled'
                    );
                END IF;
            END;
            $$
            """
        )
    else:
        status_enum.create(bind, checkfirst=True)

    # 2) create table only if it doesn't exist
    if _table_missing(bind, "task_runs"):
        op.create_table(
            "task_runs",
            sa.Column(
                "id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True
            ),
            sa.Column("pool", sa.String()),
            sa.Column("status", status_enum, nullable=False),
            sa.Column("payload", sa.JSON()),
            sa.Column("result", sa.JSON()),
            sa.Column("deps", sa.JSON(), nullable=False),
            sa.Column("edge_pred", sa.String()),
            sa.Column("labels", sa.JSON(), nullable=False),
            sa.Column("in_degree", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("config_toml", sa.String()),
            sa.Column("artifact_uri", sa.String()),
            sa.Column("started_at", sa.TIMESTAMP(timezone=True)),
            sa.Column("finished_at", sa.TIMESTAMP(timezone=True)),
        )
    # else: table already present → skip and preserve rows
    else:
        inspector = inspect(bind)
        cols = {c["name"] for c in inspector.get_columns("task_runs")}

        if "deps" not in cols:
            op.add_column(
                "task_runs",
                sa.Column("deps", sa.JSON(), nullable=False, server_default="[]"),
            )
            op.alter_column("task_runs", "deps", server_default=None)

        if "edge_pred" not in cols:
            op.add_column("task_runs", sa.Column("edge_pred", sa.String()))

        if "labels" not in cols:
            op.add_column(
                "task_runs",
                sa.Column("labels", sa.JSON(), nullable=False, server_default="[]"),
            )
            op.alter_column("task_runs", "labels", server_default=None)

        if "in_degree" not in cols:
            op.add_column(
                "task_runs",
                sa.Column(
                    "in_degree", sa.Integer(), nullable=False, server_default="0"
                ),
            )
            op.alter_column("task_runs", "in_degree", server_default=None)

        if "config_toml" not in cols:
            op.add_column("task_runs", sa.Column("config_toml", sa.String()))

        if "artifact_uri" not in cols:
            op.add_column("task_runs", sa.Column("artifact_uri", sa.String()))

        if "started_at" not in cols:
            op.add_column(
                "task_runs", sa.Column("started_at", sa.TIMESTAMP(timezone=True))
            )

        if "finished_at" not in cols:
            op.add_column(
                "task_runs", sa.Column("finished_at", sa.TIMESTAMP(timezone=True))
            )


def downgrade() -> None:
    bind = op.get_bind()
    if not _table_missing(bind, "task_runs"):
        op.drop_table("task_runs")
