"""
CLI wrapper for querying asynchronous tasks.
"""

from __future__ import annotations

import json
import time
import uuid

import httpx
import typer

from peagen.models import Status

remote_task_app = typer.Typer(help="Inspect asynchronous tasks.")


@remote_task_app.command("get")
def get(  # noqa: D401
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="UUID of the task to query"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Poll until finished"),
    interval: float = typer.Option(
        2.0, "--interval", "-i", help="Seconds between polls"
    ),
):
    """Fetch status / result for *TASK_ID* (optionally watch until done)."""

    def _rpc_call() -> dict:
        req = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "Task.get",
            "params": {"taskId": task_id},
        }
        res = httpx.post(ctx.obj.get("gateway_url"), json=req, timeout=30.0).json()
        return res["result"]

    while True:
        reply = _rpc_call()
        typer.echo(json.dumps(reply, indent=2))

        if not watch or Status.is_terminal(reply["status"]):
            break
        time.sleep(interval)


@remote_task_app.command("patch")
def patch_task(
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="UUID of the task to update"),
    changes: str = typer.Argument(..., help="JSON string of fields to modify"),
):
    """Send a Task.patch RPC call."""

    payload = json.loads(changes)
    req = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "Task.patch",
        "params": {"taskId": task_id, "changes": payload},
    }
    res = httpx.post(ctx.obj.get("gateway_url"), json=req, timeout=30.0).json()
    typer.echo(json.dumps(res["result"], indent=2))


def _simple_call(ctx: typer.Context, method: str, selector: str) -> None:
    req = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,
        "params": {"selector": selector},
    }
    res = httpx.post(ctx.obj.get("gateway_url"), json=req, timeout=30.0).json()
    typer.echo(json.dumps(res["result"], indent=2))


@remote_task_app.command("pause")
def pause(
    ctx: typer.Context,
    selector: str = typer.Argument(..., help="Task ID or label selector"),
) -> None:
    """Pause one task or all tasks matching a label."""
    _simple_call(ctx, "Task.pause", selector)


@remote_task_app.command("resume")
def resume(
    ctx: typer.Context,
    selector: str = typer.Argument(..., help="Task ID or label selector"),
) -> None:
    """Resume a paused task or label set."""
    _simple_call(ctx, "Task.resume", selector)


@remote_task_app.command("cancel")
def cancel(
    ctx: typer.Context,
    selector: str = typer.Argument(..., help="Task ID or label selector"),
) -> None:
    """Cancel a task or label set."""
    _simple_call(ctx, "Task.cancel", selector)


@remote_task_app.command("retry")
def retry(
    ctx: typer.Context,
    selector: str = typer.Argument(..., help="Task ID or label selector"),
) -> None:
    """Retry a task or label set."""
    _simple_call(ctx, "Task.retry", selector)


@remote_task_app.command("retry-from")
def retry_from(
    ctx: typer.Context,
    selector: str = typer.Argument(..., help="Task ID or label selector"),
) -> None:
    """Retry a task and its descendants."""
    _simple_call(ctx, "Task.retry_from", selector)
