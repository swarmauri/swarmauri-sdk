"""Database management commands."""

from __future__ import annotations

import asyncio
import uuid

import httpx


from pathlib import Path

import typer

from peagen.handlers.migrate_handler import migrate_handler

from peagen.schemas import TaskCreate
from peagen.protocols import Request


# ``alembic.ini`` lives in the package root next to ``migrations``.
# When running from source the module sits one directory deeper than
# an installed wheel. Check both possible locations for robustness.
_src_cfg = Path(__file__).resolve().parents[3] / "alembic.ini"
_pkg_cfg = Path(__file__).resolve().parents[2] / "alembic.ini"
ALEMBIC_CFG = _src_cfg if _src_cfg.exists() else _pkg_cfg

DEFAULT_GATEWAY = (
    "http://localhost:8000/rpc"  # replace with peagen.defaults to make consistency
)

# DEFAULT_GATEWAY = defaults.CONFIG["gateway_url"]


local_db_app = typer.Typer(help="Database utilities.")
remote_db_app = typer.Typer(help="Database utilities via JSON-RPC.")


def _submit_task(op: str, gateway_url: str, message: str | None = None) -> str:
    """Submit a migration *op* via JSON-RPC and return the task id."""
    args = {"op": op, "alembic_ini": str(ALEMBIC_CFG)}
    if message:
        args["message"] = message
    task = TaskCreate(
        id=str(uuid.uuid4()),
        pool="default",
        payload={"action": "migrate", "args": args},
    )
    envelope = Request(
        id=task.id,
        method="Task.submit",
        params={
            "pool": task.pool,
            "payload": task.payload,
            "taskId": task.id,
        },
    )
    resp = httpx.post(gateway_url, json=envelope.model_dump(), timeout=10.0)
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return str(data.get("result", {}).get("taskId", task.id))


@local_db_app.command("upgrade")
def upgrade() -> None:
    """Apply Alembic migrations up to HEAD."""
    typer.echo(f"Running alembic -c {ALEMBIC_CFG} upgrade head …")
    task = {
        "pool": "default",
        "payload": {
            "action": "migrate",
            "args": {"op": "upgrade", "alembic_ini": str(ALEMBIC_CFG)},
        },
    }
    result = asyncio.run(migrate_handler(task))
    if stdout := result.get("stdout"):
        typer.echo(stdout)
    if stderr := result.get("stderr"):
        typer.echo(stderr, err=True)
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
    task = {
        "pool": "default",
        "payload": {
            "action": "migrate",
            "args": {
                "op": "revision",
                "message": message,
                "alembic_ini": str(ALEMBIC_CFG),
            },
        },
    }
    result = asyncio.run(migrate_handler(task))
    if stdout := result.get("stdout"):
        typer.echo(stdout)
    if stderr := result.get("stderr"):
        typer.echo(stderr, err=True)
    if not result.get("ok", False):
        typer.echo(f"[ERROR] {result.get('error')}")
        raise typer.Exit(1)


@local_db_app.command("downgrade")
def downgrade() -> None:
    """Downgrade the database by one revision."""
    typer.echo(f"Running alembic -c {ALEMBIC_CFG} downgrade -1 …")
    task = {
        "pool": "default",
        "payload": {
            "action": "migrate",
            "args": {"op": "downgrade", "alembic_ini": str(ALEMBIC_CFG)},
        },
    }
    result = asyncio.run(migrate_handler(task))
    if stdout := result.get("stdout"):
        typer.echo(stdout)
    if stderr := result.get("stderr"):
        typer.echo(stderr, err=True)
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
