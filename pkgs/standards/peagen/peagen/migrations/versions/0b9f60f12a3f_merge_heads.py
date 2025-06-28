"""merge spec_hash and automated revision heads"""

from typing import Sequence, Union

revision = "0b9f60f12a3f"
down_revision: Union[str, Sequence[str], None] = ("abcd1234efgh", "97a9f54587b2")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
