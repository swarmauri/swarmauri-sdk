from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "c1a2b3c4d5e6"
down_revision = "c3f9a1d1855a"


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("task_runs")}
    if "oids" not in cols:
        op.add_column("task_runs", sa.Column("oids", sa.JSON()))
    if "artifact_uri" in cols:
        op.drop_column("task_runs", "artifact_uri")


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("task_runs")}
    if "artifact_uri" not in cols:
        op.add_column("task_runs", sa.Column("artifact_uri", sa.String()))
    if "oids" in cols:
        op.drop_column("task_runs", "oids")
