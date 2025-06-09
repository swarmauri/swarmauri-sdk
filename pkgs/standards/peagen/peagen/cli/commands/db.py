
"""Database management commands."""

from __future__ import annotations

import subprocess

import typer

local_db_app = typer.Typer(help="Database utilities.")


@local_db_app.command("upgrade")
def upgrade() -> None:
    """Apply Alembic migrations up to HEAD."""
    typer.echo("Running alembic upgrade head …")
    subprocess.run(["alembic", "upgrade", "head"], check=True)
