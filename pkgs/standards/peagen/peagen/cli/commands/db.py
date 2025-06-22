"""Database management commands."""

from __future__ import annotations

import asyncio
from pathlib import Path
import uuid

import httpx

import typer

from peagen.handlers.migrate_handler import migrate_handler
from peagen.models import Task

# ``alembic.ini`` lives in ``pkgs/standards/peagen`` next to ``migrations``.
# ``db.py`` sits under ``peagen/cli/commands``. Climbing three directories
# resolves to the package root whether running from source or an installed
# wheel.
ALEMBIC_CFG = Path(__file__).resolve().parents[3] / "alembic.ini"

DEFAULT_GATEWAY = "http://localhost:8000/rpc"

local_db_app = typer.Typer(help="Database utilities.")
remote_db_app = typer.Typer(help="Database utilities via JSON-RPC.")


def _submit_task(op: str, gateway_url: str, message: str | None = None) -> str:
    """Submit a migration *op* via JSON-RPC and return the task id."""
    args = {"op": op, "alembic_ini": str(ALEMBIC_CFG)}
    if message:
        args["message"] = message
    task = Task(
        id=str(uuid.uuid4()),
        pool="default",
        payload={"action": "migrate", "args": args},
    )
    envelope = {
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {"pool": task.pool, "payload": task.payload},
    }
    resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return str(data.get("id", task.id))


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


@remote_db_app.command("upgrade")
def remote_upgrade(
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
) -> None:
    """Submit an upgrade task via JSON-RPC."""
    try:
        task_id = _submit_task("upgrade", gateway_url)
        typer.echo(f"Submitted upgrade → taskId={task_id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


@remote_db_app.command("revision")
def remote_revision(
    message: str = typer.Option(
        "init", "--message", "-m", help="Message for the new revision"
    ),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
) -> None:
    """Submit a revision task via JSON-RPC."""
    try:
        task_id = _submit_task("revision", gateway_url, message)
        typer.echo(f"Submitted revision → taskId={task_id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


@remote_db_app.command("downgrade")
def remote_downgrade(
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
) -> None:
    """Submit a downgrade task via JSON-RPC."""
    try:
        task_id = _submit_task("downgrade", gateway_url)
        typer.echo(f"Submitted downgrade → taskId={task_id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)
