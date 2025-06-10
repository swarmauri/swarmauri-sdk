
"""Database management commands."""

from __future__ import annotations

import subprocess

import typer

local_db_app = typer.Typer(help="Database utilities.")


@local_db_app.command("upgrade")
def upgrade() -> None:
    """Apply Alembic migrations up to HEAD."""
    typer.echo(
        "Running alembic -c pkgs/standards/peagen/alembic.ini upgrade head …"
    )
    subprocess.run(
        [
            "alembic",
            "-c",
            "pkgs/standards/peagen/alembic.ini",
            "upgrade",
            "head",
        ],
        check=True,
    )


@local_db_app.command("revision")
def revision() -> None:
    """Generate a new Alembic revision."""
    typer.echo(
        "Running alembic -c pkgs/standards/peagen/alembic.ini revision --autogenerate -m 'init' …"
    )
    try:
        subprocess.run(
            [
                "alembic",
                "-c",
                "pkgs/standards/peagen/alembic.ini",
                "revision",
                "--autogenerate",
                "-m",
                "init",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


@local_db_app.command("downgrade")
def downgrade() -> None:
    """Downgrade the database by one revision."""
    typer.echo(
        "Running alembic -c pkgs/standards/peagen/alembic.ini downgrade -1 …"
    )
    try:
        subprocess.run(
            [
                "alembic",
                "-c",
                "pkgs/standards/peagen/alembic.ini",
                "downgrade",
                "-1",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)
