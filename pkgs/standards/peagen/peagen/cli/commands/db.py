"""Database management commands."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer

from peagen.handlers.migrate_handler import migrate_handler
from peagen.models import Task

# ``alembic.ini`` lives in the package root next to ``migrations``. Using
# ``parents[2]`` works whether running from source or an installed wheel.
ALEMBIC_CFG = Path(__file__).resolve().parents[2] / "alembic.ini"

local_db_app = typer.Typer(help="Database utilities.")


@local_db_app.command("upgrade")
def upgrade() -> None:
    """Apply Alembic migrations up to HEAD."""
    typer.echo(f"Running alembic -c {ALEMBIC_CFG} upgrade head …")
    task = Task(
        pool="default",
        payload={
            "action": "migrate",
            "args": {"op": "upgrade", "alembic_ini": str(ALEMBIC_CFG)},
        },
    )
    result = asyncio.run(migrate_handler(task))
    if not result.get("ok", False):
        typer.echo(f"[ERROR] {result.get('error')}")
        raise typer.Exit(1)


@local_db_app.command("revision")
def revision(
    message: str = typer.Option(
        "init",
        "--message",
        "-m",
        help="Message for the new revision",
    ),
) -> None:
    """Generate a new Alembic revision."""
    typer.echo(
        f"Running alembic -c {ALEMBIC_CFG} revision --autogenerate -m '{message}' …"
    )
    task = Task(
        pool="default",
        payload={
            "action": "migrate",
            "args": {
                "op": "revision",
                "message": message,
                "alembic_ini": str(ALEMBIC_CFG),
            },
        },
    )
    result = asyncio.run(migrate_handler(task))
    if not result.get("ok", False):
        typer.echo(f"[ERROR] {result.get('error')}")
        raise typer.Exit(1)


@local_db_app.command("downgrade")
def downgrade() -> None:
    """Downgrade the database by one revision."""
    typer.echo(f"Running alembic -c {ALEMBIC_CFG} downgrade -1 …")
    task = Task(
        pool="default",
        payload={
            "action": "migrate",
            "args": {"op": "downgrade", "alembic_ini": str(ALEMBIC_CFG)},
        },
    )
    result = asyncio.run(migrate_handler(task))
    if not result.get("ok", False):
        typer.echo(f"[ERROR] {result.get('error')}")
        raise typer.Exit(1)
