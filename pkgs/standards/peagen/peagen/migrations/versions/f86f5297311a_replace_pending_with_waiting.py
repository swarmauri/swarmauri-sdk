from alembic import op
import sqlalchemy as sa

revision = "f86f5297311a"
down_revision = "f2a4b3c5d6e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text("UPDATE task_runs SET status='waiting' WHERE status='pending'")
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text("UPDATE task_runs SET status='pending' WHERE status='waiting'")
    )
