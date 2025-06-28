"""ensure tenants table exists"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import UUID

revision: str = "851bf7d3ad61"
down_revision: Union[str, Sequence[str], None] = "0b9f60f12a3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tenants table if missing."""
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


def downgrade() -> None:
    """Drop tenants table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    if "tenants" in inspector.get_table_names():
        op.drop_table("tenants")
