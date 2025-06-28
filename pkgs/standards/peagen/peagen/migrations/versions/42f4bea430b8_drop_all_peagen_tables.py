from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "42f4bea430b8"
down_revision = "1e31bf9cf06b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    for table in inspector.get_table_names():
        if table != "alembic_version":
            op.execute(sa.text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))


def downgrade() -> None:
    # irreversible
    pass
