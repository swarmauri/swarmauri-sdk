"""add new columns to task_runs"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20240502"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("task_runs", sa.Column("deps", sa.JSON(), nullable=True))
    op.add_column("task_runs", sa.Column("edge_pred", sa.String(), nullable=True))
    op.add_column("task_runs", sa.Column("labels", sa.JSON(), nullable=True))
    op.add_column("task_runs", sa.Column("interface_args", sa.JSON(), nullable=True))
    op.add_column("task_runs", sa.Column("config_toml", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("task_runs", "config_toml")
    op.drop_column("task_runs", "interface_args")
    op.drop_column("task_runs", "labels")
    op.drop_column("task_runs", "edge_pred")
    op.drop_column("task_runs", "deps")
