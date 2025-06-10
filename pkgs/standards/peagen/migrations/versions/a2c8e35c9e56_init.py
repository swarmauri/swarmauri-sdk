"""init

Revision ID: a2c8e35c9e56
Revises: 83262a8eda95
Create Date: 2025-06-10 00:13:18.489932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2c8e35c9e56'
down_revision: Union[str, None] = '83262a8eda95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
