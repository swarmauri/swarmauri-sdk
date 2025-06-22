from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import UUID

revision = "d2e5dfb3c4f0"
down_revision = "c3f9a1d1855a"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return
    inspector = inspect(bind)
    if "task_runs" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("task_runs")}
        if "tenant_id" not in cols:
            op.add_column(
                "task_runs",
                sa.Column(
                    "tenant_id",
                    UUID(as_uuid=True),
                    nullable=False,
                    server_default="00000000-0000-0000-0000-000000000000",
                ),
            )
            op.execute(
                "UPDATE task_runs SET tenant_id = '00000000-0000-0000-0000-000000000000'"
            )
            if bind.dialect.name != "sqlite":
                op.alter_column("task_runs", "tenant_id", server_default=None)
        if "project_id" not in cols:
            op.add_column(
                "task_runs",
                sa.Column("project_id", UUID(as_uuid=True), nullable=True),
            )
        pk = inspector.get_pk_constraint("task_runs")
        if pk and pk["constrained_columns"] == ["id"]:
            op.drop_constraint(pk["name"], "task_runs", type_="primary")
            op.create_primary_key(None, "task_runs", ["id", "tenant_id"])


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return
    inspector = inspect(bind)
    if "task_runs" in inspector.get_table_names():
        pk = inspector.get_pk_constraint("task_runs")
        if pk and set(pk["constrained_columns"]) == {"id", "tenant_id"}:
            op.drop_constraint(pk["name"], "task_runs", type_="primary")
            op.create_primary_key(None, "task_runs", ["id"])
        cols = {c["name"] for c in inspector.get_columns("task_runs")}
        if "project_id" in cols:
            op.drop_column("task_runs", "project_id")
        if "tenant_id" in cols:
            op.drop_column("task_runs", "tenant_id")
