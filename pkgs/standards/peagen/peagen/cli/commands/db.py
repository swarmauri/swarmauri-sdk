
"""Database management commands."""

from __future__ import annotations

import subprocess
from pathlib import Path

import typer

ALEMBIC_CFG = Path(__file__).resolve().parents[3] / "alembic.ini"

local_db_app = typer.Typer(help="Database utilities.")


@local_db_app.command("upgrade")
def upgrade() -> None:
    """Apply Alembic migrations up to HEAD."""
    typer.echo(f"Running alembic -c {ALEMBIC_CFG} upgrade head …")
    subprocess.run(
        [
            "alembic",
            "-c",
            str(ALEMBIC_CFG),
            "upgrade",
            "head",
        ],
        check=True,
    )


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
    try:
        subprocess.run(
            [
                "alembic",
                "-c",
                str(ALEMBIC_CFG),
                "revision",
                "--autogenerate",
                "-m",
                message,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


@local_db_app.command("downgrade")
def downgrade() -> None:
    """Downgrade the database by one revision."""
    typer.echo(f"Running alembic -c {ALEMBIC_CFG} downgrade -1 …")
    try:
        subprocess.run(
            [
                "alembic",
                "-c",
                str(ALEMBIC_CFG),
                "downgrade",
                "-1",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)
