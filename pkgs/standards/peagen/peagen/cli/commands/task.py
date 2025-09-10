"""
CLI wrapper for querying and managing asynchronous Tasks via Tigrbl.
"""

from __future__ import annotations

import json
import time

import typer
from tigrbl_client import TigrblClient
from tigrbl import get_schema
from peagen.orm import Status, Task
from peagen.cli.task_helpers import get_task, build_task, submit_task

remote_task_app = typer.Typer(help="Inspect asynchronous tasks.")


# ───────────────────────── helpers ────────────────────────────────────
def _rpc(ctx: typer.Context) -> TigrblClient:
    return ctx.obj["rpc"]


def _schema(tag: str):
    # shortcut to the Pydantic model generated for <Task, tag>
    return get_schema(Task, tag)


# ───────────────────────── commands ───────────────────────────────────
@remote_task_app.command("get")
def get(  # noqa: D401
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="UUID of the task to query"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Poll until finished"),
    interval: float = typer.Option(
        2.0, "--interval", "-i", help="Seconds between polls"
    ),
):
    """Fetch status/result for *TASK_ID* (optionally watch until done)."""
    while True:
        reply = get_task(_rpc(ctx), task_id)
        typer.echo(json.dumps(reply, indent=2))

        if not watch or Status.is_terminal(reply["status"]):
            break
        time.sleep(interval)


@remote_task_app.command("patch")
def patch_task(
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="UUID of the task to update"),
    changes: str = typer.Argument(..., help="JSON dict of fields to modify"),
):
    """Apply partial update to a Task."""
    SUpdate = _schema("update")
    SRead = _schema("read")

    changes_obj = SUpdate.model_validate(json.loads(changes))
    params = {"id": task_id, **changes_obj.model_dump(exclude_unset=True)}

    rpc = _rpc(ctx)
    res = rpc.call("Tasks.update", params=params, out_schema=SRead)
    typer.echo(json.dumps(res.model_dump(), indent=2))


# ── helper for one-shot status transitions ────────────────────────────
def _simple_status_change(ctx: typer.Context, task_id: str, new_status: Status):
    SUpdate = _schema("update")
    SRead = _schema("read")
    params = {"id": task_id, "status": new_status}

    rpc = _rpc(ctx)
    res = rpc.call("Tasks.update", params=SUpdate(**params), out_schema=SRead)
    typer.echo(json.dumps(res.model_dump(), indent=2))


@remote_task_app.command("pause")
def pause(ctx: typer.Context, task_id: str):
    """Mark a running task as *paused*."""
    _simple_status_change(ctx, task_id, Status.paused)


@remote_task_app.command("resume")
def resume(ctx: typer.Context, task_id: str):
    """Resume a paused task."""
    _simple_status_change(ctx, task_id, Status.running)


@remote_task_app.command("cancel")
def cancel(ctx: typer.Context, task_id: str):
    """Cancel a running/queued task."""
    _simple_status_change(ctx, task_id, Status.cancelled)


@remote_task_app.command("retry")
def retry(ctx: typer.Context, task_id: str):
    """Retry a task (sets status = retry)."""
    _simple_status_change(ctx, task_id, Status.retry)


@remote_task_app.command("retry-from")
def retry_from(
    ctx: typer.Context,
    source_task_id: str = typer.Argument(..., help="Existing task to clone"),
):
    """
    Create a **new** task by cloning *source_task_id* and submitting it.

    Works with the new flat schema where `action` and `args` live directly
    on the Task row (rather than inside `payload`).
    """
    # 1. fetch the original task
    original = get_task(_rpc(ctx), source_task_id)
    if not original.get("action"):
        typer.echo("Source task has no action to clone.", err=True)
        raise typer.Exit(1)

    # 2. build & submit a new task with the same action/args/pool
    new_task = build_task(
        action=original["action"],
        args=original.get("args", {}),
        pool_id=original.get("pool_id", "default"),
        labels=original.get("labels") or [],
        repo=original.get("repo", ""),
        ref=original.get("ref", "HEAD"),
    )
    submitted = submit_task(_rpc(ctx), new_task)
    typer.echo(json.dumps(submitted, indent=2))
