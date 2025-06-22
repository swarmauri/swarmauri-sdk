from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "9b2c3d4e5f6a"
down_revision = "f86f5297311a"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "abuse_records" not in inspector.get_table_names():
        op.create_table(
            "abuse_records",
            sa.Column("ip", sa.String(), primary_key=True),
            sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column(
                "first_seen",
                sa.TIMESTAMP(timezone=True),
                nullable=False,
            ),
            sa.Column(
                "banned", sa.Boolean(), nullable=False, server_default=sa.text("false")
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "abuse_records" in inspector.get_table_names():
        op.drop_table("abuse_records")
