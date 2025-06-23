from alembic import op
import sqlalchemy as sa

revision = "f86f5297311a"
down_revision = "f2a4b3c5d6e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add ``waiting`` to the enum and migrate rows."""

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(sa.text("ALTER TYPE status ADD VALUE IF NOT EXISTS 'waiting'"))
    if bind.dialect.name == "postgresql":
        pending = "status::text='pending'"
    else:
        pending = "status='pending'"
    bind.execute(sa.text(f"UPDATE task_runs SET status='waiting' WHERE {pending}"))


def downgrade() -> None:
    """Revert row updates; keep enum values intact."""

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        waiting = "status::text='waiting'"
    else:
        waiting = "status='waiting'"
    bind.execute(sa.text(f"UPDATE task_runs SET status='pending' WHERE {waiting}"))
