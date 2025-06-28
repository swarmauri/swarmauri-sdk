from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import UUID

revision = "1e31bf9cf06b"
down_revision = "0b9f60f12a3f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "tenants" not in inspector.get_table_names():
        op.create_table(
            "tenants",
            sa.Column("id", UUID(as_uuid=True), primary_key=True),
            sa.Column("slug", sa.String(), nullable=False, unique=True),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("date_created", sa.DateTime(timezone=True), nullable=False),
            sa.Column("last_modified", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "tenants" in inspector.get_table_names():
        op.drop_index("ix_tenants_slug", table_name="tenants")
        op.drop_table("tenants")
