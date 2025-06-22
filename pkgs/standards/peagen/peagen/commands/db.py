"""Database migration commands for Peagen."""

from __future__ import annotations

from pathlib import Path

import typer
from alembic import command
from alembic.config import Config


db_app = typer.Typer(help="Manage Peagen database migrations.")


def _alembic_config() -> Config:
    """Return Alembic Config pointing to package alembic.ini."""
    ini_path = Path(__file__).resolve().parents[1] / "alembic.ini"
    return Config(str(ini_path))


@db_app.command("upgrade")
def upgrade(revision: str = "head") -> None:
    """Upgrade local database to a given revision (default: head)."""
    cfg = _alembic_config()
    typer.echo(f"Upgrading local database to {revision} …")
    command.upgrade(cfg, revision)
    typer.echo("✅  Upgrade complete.")


@db_app.command("downgrade")
def downgrade(revision: str = "-1") -> None:
    """Downgrade local database to a given revision (default: -1)."""
    cfg = _alembic_config()
    typer.echo(f"Downgrading local database to {revision} …")
    command.downgrade(cfg, revision)
    typer.echo("✅  Downgrade complete.")
