from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "a6cc5b24ad5c"
down_revision = "ae1de73e4143"


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("task_runs")}
    if "commit_hexsha" not in cols:
        op.add_column("task_runs", sa.Column("commit_hexsha", sa.String()))


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("task_runs")}
    if "commit_hexsha" in cols:
        op.drop_column("task_runs", "commit_hexsha")
