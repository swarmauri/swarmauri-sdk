from alembic import op
import sqlalchemy as sa

revision = "f91bd40d0972"
down_revision = "f86f5297311a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Update pending statuses for SQLite and Postgres."""

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(
            sa.text(
                "UPDATE task_runs SET status='waiting' WHERE status::text='pending'"
            )
        )
    else:
        bind.execute(
            sa.text("UPDATE task_runs SET status='waiting' WHERE status='pending'")
        )


def downgrade() -> None:
    """Revert row updates."""

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(
            sa.text(
                "UPDATE task_runs SET status='pending' WHERE status::text='waiting'"
            )
        )
    else:
        bind.execute(
            sa.text("UPDATE task_runs SET status='pending' WHERE status='waiting'")
        )
