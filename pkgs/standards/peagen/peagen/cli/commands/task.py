"""
CLI wrapper for querying and managing asynchronous Tasks via AutoAPI.
"""

from __future__ import annotations

import json, time, uuid, typer, httpx
from typing import Any

from autoapi_client import AutoAPIClient
from autoapi          import AutoAPI
from peagen.orm import Status, Task
from peagen.cli.task_helpers import get_task_result, build_task, submit_task

remote_task_app = typer.Typer(help="Inspect asynchronous tasks.")


# ───────────────────────── helpers ────────────────────────────────────
def _rpc(ctx: typer.Context) -> AutoAPIClient:
    return AutoAPIClient(ctx.obj["gateway_url"])


def _schema(tag: str):
    return AutoAPI.get_schema(Task, tag)          # classmethod


# ───────────────────────── commands ───────────────────────────────────
@remote_task_app.command("get")
def get(                                          # noqa: D401
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="UUID of the task to query"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Poll until finished"),
    interval: float = typer.Option(2.0, "--interval", "-i", help="Seconds between polls"),
):
    """Fetch status/result for TASK_ID (optionally watch until done)."""
    while True:
        reply = get_task_result(task_id, gateway_url=ctx.obj["gateway_url"])
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
    SRead   = _schema("read")

    changes_obj = SUpdate.model_validate(json.loads(changes))
    params      = {"id": task_id, **changes_obj.model_dump(exclude_unset=True)}

    with _rpc(ctx) as rpc:
        res = rpc.call("Tasks.update", params=params, out_schema=SRead)
    typer.echo(json.dumps(res.model_dump(), indent=2))


# ── helper for one-shot status transitions ────────────────────────────
def _simple_status_change(ctx: typer.Context, task_id: str, new_status: Status):
    SUpdate = _schema("update")
    SRead   = _schema("read")
    params  = {"id": task_id, "status": new_status}

    with _rpc(ctx) as rpc:
        res = rpc.call("Tasks.update", params=SUpdate(**params), out_schema=SRead)
    typer.echo(json.dumps(res.model_dump(), indent=2))


@remote_task_app.command("pause")
def pause(ctx: typer.Context, task_id: str):
    """Mark a running task as paused."""
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
    """Retry a task (sets status=retry)."""
    _simple_status_change(ctx, task_id, Status.retry)


@remote_task_app.command("retry-from")
def retry_from(
    ctx: typer.Context,
    source_task_id: str = typer.Argument(..., help="Existing task to clone"),
):
    """Create a **new** task by cloning *source_task_id* and submitting it."""
    # 1. fetch original
    original = get_task_result(source_task_id, gateway_url=ctx.obj["gateway_url"])
    if not original["result"]:
        typer.echo("Source task has no payload/result to clone.", err=True)
        raise typer.Exit(1)

    # 2. build & submit new task
    payload: dict[str, Any] = original["result"]["payload"]  # type: ignore[index]
    new_task = build_task(
        action=payload["action"],
        args=payload["args"],
        pool=original.get("pool", "default"),
        tenant_id=original.get("tenant_id", "default"),
    )
    submitted = submit_task(ctx.obj["gateway_url"], new_task)
    typer.echo(json.dumps(submitted, indent=2))
