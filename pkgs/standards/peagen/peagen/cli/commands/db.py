"""Database management commands."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx

import typer

from peagen.handlers.migrate_handler import migrate_handler
from peagen.models import Task

# ``alembic.ini`` lives in ``pkgs/standards/peagen`` next to ``migrations``.
# ``db.py`` sits under ``peagen/cli/commands``. Climbing three directories
# resolves to the package root whether running from source or an installed
# wheel.
ALEMBIC_CFG = Path(__file__).resolve().parents[3] / "alembic.ini"

local_db_app = typer.Typer(help="Database utilities.")
remote_db_app = typer.Typer(help="Database utilities via JSON-RPC.")


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


def _submit(ctx: typer.Context, op: str, message: str | None = None) -> str:
    args = {"op": op, "alembic_ini": str(ALEMBIC_CFG)}
    if message:
        args["message"] = message
    task = Task(pool="default", payload={"action": "migrate", "args": args})
    envelope = {
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {"taskId": task.id, "pool": task.pool, "payload": task.payload},
    }
    resp = httpx.post(ctx.obj.get("gateway_url"), json=envelope, timeout=30.0)
    resp.raise_for_status()
    reply = resp.json()
    if "error" in reply:
        typer.secho(
            f"Remote error {reply['error']['code']}: {reply['error']['message']}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)
    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
    if reply.get("result"):
        typer.echo(json.dumps(reply["result"], indent=2))
    return task.id


@remote_db_app.command("upgrade")
def remote_upgrade(ctx: typer.Context) -> None:
    """Submit an upgrade task via JSON-RPC."""
    _submit(ctx, "upgrade")


@remote_db_app.command("revision")
def remote_revision(
    ctx: typer.Context,
    message: str = typer.Option(
        "init",
        "--message",
        "-m",
        help="Message for the new revision",
    ),
) -> None:
    """Submit a revision task via JSON-RPC."""
    _submit(ctx, "revision", message)


@remote_db_app.command("downgrade")
def remote_downgrade(ctx: typer.Context) -> None:
    """Submit a downgrade task via JSON-RPC."""
    _submit(ctx, "downgrade")
