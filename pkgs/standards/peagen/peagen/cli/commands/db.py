"""Database management commands."""

from __future__ import annotations

import asyncio


from pathlib import Path

import typer

from peagen.handlers.migrate_handler import migrate_handler

from peagen.cli.task_helpers import build_task, submit_task


# ``alembic.ini`` lives in the package root next to ``migrations``.
# When running from source the module sits one directory deeper than
# an installed wheel. Check both possible locations for robustness.
_src_cfg = Path(__file__).resolve().parents[3] / "alembic.ini"
_pkg_cfg = Path(__file__).resolve().parents[2] / "alembic.ini"
ALEMBIC_CFG = _src_cfg if _src_cfg.exists() else _pkg_cfg


local_db_app = typer.Typer(help="Database utilities.")
remote_db_app = typer.Typer(help="Database utilities via JSON-RPC.")


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
    ctx: typer.Context,
) -> None:
    """Submit an upgrade task via JSON-RPC."""
    try:
        task = build_task(
            "migrate",
            {"op": "upgrade", "alembic_ini": str(ALEMBIC_CFG)},
            pool="default",
        )
        reply = submit_task(ctx.obj["rpc"], task)
        if "error" in reply:
            raise RuntimeError(reply["error"]["message"])
        task_id = reply.get("result", {}).get("taskId", task.id)
        typer.echo(f"Submitted upgrade → taskId={task_id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


@remote_db_app.command("revision")
def remote_revision(
    ctx: typer.Context,
    message: str = typer.Option(
        "init", "--message", "-m", help="Message for the new revision"
    ),
) -> None:
    """Submit a revision task via JSON-RPC."""
    try:
        task = build_task(
            "migrate",
            {
                "op": "revision",
                "message": message,
                "alembic_ini": str(ALEMBIC_CFG),
            },
            pool="default",
        )
        reply = submit_task(ctx.obj["rpc"], task)
        if "error" in reply:
            raise RuntimeError(reply["error"]["message"])
        task_id = reply.get("result", {}).get("taskId", task.id)
        typer.echo(f"Submitted revision → taskId={task_id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)


@remote_db_app.command("downgrade")
def remote_downgrade(
    ctx: typer.Context,
) -> None:
    """Submit a downgrade task via JSON-RPC."""
    try:
        task = build_task(
            "migrate",
            {"op": "downgrade", "alembic_ini": str(ALEMBIC_CFG)},
            pool="default",
        )
        reply = submit_task(ctx.obj["rpc"], task)
        if "error" in reply:
            raise RuntimeError(reply["error"]["message"])
        task_id = reply.get("result", {}).get("taskId", task.id)
        typer.echo(f"Submitted downgrade → taskId={task_id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] {exc}")
        raise typer.Exit(1)
