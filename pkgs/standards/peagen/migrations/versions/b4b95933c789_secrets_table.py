from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "b4b95933c789"
down_revision = "0001"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "secrets" not in inspector.get_table_names():
        op.create_table(
            "secrets",
            sa.Column("tenant_id", sa.String(), primary_key=True),
            sa.Column("owner_fpr", sa.String(), nullable=False),
            sa.Column("name", sa.String(), primary_key=True),
            sa.Column("cipher", sa.String(), nullable=False),
            sa.Column("created_at", sa.TIMESTAMP(timezone=True)),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "secrets" in inspector.get_table_names():
        op.drop_table("secrets")
