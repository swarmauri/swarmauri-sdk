"""
CLI wrapper for querying asynchronous tasks.
"""

from __future__ import annotations

import json
import time
import uuid

import httpx
import typer

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

        if not watch or reply["status"] in {"finished", "failed"}:
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


def _simple_rpc(ctx: typer.Context, method: str, params: dict) -> None:
    req = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method, "params": params}
    res = httpx.post(ctx.obj.get("gateway_url"), json=req, timeout=30.0).json()
    typer.echo(json.dumps(res.get("result", res), indent=2))


def _id_or_label(identifier: str) -> tuple[str, str]:
    """Return parameter key/value for task or label identifier."""
    try:
        uuid.UUID(identifier)
        return "taskId", identifier
    except ValueError:
        return "label", identifier


@remote_task_app.command("pause")
def pause(ctx: typer.Context, identifier: str = typer.Argument(...)):
    """Pause a running task."""
    key, value = _id_or_label(identifier)
    _simple_rpc(ctx, "Task.pause", {key: value})


@remote_task_app.command("resume")
def resume(ctx: typer.Context, identifier: str = typer.Argument(...)):
    """Resume a paused task."""
    key, value = _id_or_label(identifier)
    _simple_rpc(ctx, "Task.resume", {key: value})


@remote_task_app.command("cancel")
def cancel(ctx: typer.Context, identifier: str = typer.Argument(...)):
    """Cancel a task."""
    key, value = _id_or_label(identifier)
    _simple_rpc(ctx, "Task.cancel", {key: value})


@remote_task_app.command("retry")
def retry(ctx: typer.Context, identifier: str = typer.Argument(...)):
    """Retry a task from the beginning."""
    key, value = _id_or_label(identifier)
    _simple_rpc(ctx, "Task.retry", {key: value})


@remote_task_app.command("retry-from")
def retry_from(ctx: typer.Context, identifier: str = typer.Argument(...), start_idx: int = typer.Argument(...)):
    """Retry a task from a specific index."""
    key, value = _id_or_label(identifier)
    _simple_rpc(ctx, "Task.retryFrom", {key: value, "start_idx": start_idx})
