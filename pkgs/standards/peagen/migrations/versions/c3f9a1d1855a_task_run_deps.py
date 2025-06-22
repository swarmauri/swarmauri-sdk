from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text

revision = "c3f9a1d1855a"
down_revision = "b4b95933c789"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "task_run_deps" not in inspector.get_table_names():
        op.create_table(
            "task_run_deps",
            sa.Column(
                "task_id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True
            ),
            sa.Column(
                "dep_id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True
            ),
        )

    if "task_runs" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("task_runs")}
        if "deps" in cols:
            rows = list(bind.execute(text("SELECT id, deps FROM task_runs")))
            for row in rows:
                deps = row[1] or []
                for dep in deps:
                    bind.execute(
                        text(
                            "INSERT INTO task_run_deps (task_id, dep_id) VALUES (:t, :d) ON CONFLICT DO NOTHING"
                        ),
                        {"t": row[0], "d": dep},
                    )
            op.drop_column("task_runs", "deps")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "task_run_deps" in inspector.get_table_names():
        op.add_column(
            "task_runs",
            sa.Column("deps", sa.JSON(), nullable=False, server_default="[]"),
        )
        rows = list(bind.execute(text("SELECT task_id, dep_id FROM task_run_deps")))
        for task_id, dep_id in rows:
            bind.execute(
                text(
                    "UPDATE task_runs SET deps = COALESCE(deps, '[]'::jsonb) || to_jsonb(:d) WHERE id = :t"
                ),
                {"t": task_id, "d": dep_id},
            )
        op.alter_column("task_runs", "deps", server_default=None)
        op.drop_table("task_run_deps")
