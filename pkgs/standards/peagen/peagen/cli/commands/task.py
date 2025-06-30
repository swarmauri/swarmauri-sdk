"""
CLI wrapper for querying asynchronous tasks.
"""

from __future__ import annotations

import json
import time
import uuid

import httpx


import typer

from peagen.transport import (
    TASK_PATCH,
    TASK_PAUSE,
    TASK_RESUME,
    TASK_CANCEL,
    TASK_RETRY,
    TASK_RETRY_FROM,
)
from peagen.transport.jsonrpc_schemas.task import (
    PatchParams,
    PatchResult,
    SimpleSelectorParams,
    CountResult,
)
from peagen.cli.task_helpers import get_task
from peagen.transport import Request, Response

from peagen.transport.jsonrpc_schemas import Status

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

    while True:
        reply = get_task(ctx.obj.get("gateway_url"), task_id)
        typer.echo(json.dumps(reply.model_dump(), indent=2))

        if not watch or Status.is_terminal(reply.status) or reply.result is not None:
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
    envelope = Request(
        id=str(uuid.uuid4()),
        method=TASK_PATCH,
        params=PatchParams(taskId=task_id, changes=payload).model_dump(),
    )
    resp = httpx.post(
        ctx.obj.get("gateway_url"),
        json=envelope.model_dump(mode="json"),
        timeout=30.0,
    )
    resp.raise_for_status()
    # ``resp.json()`` already returns a parsed dictionary. ``model_validate_json``
    # expects a JSON string, so use ``model_validate`` to validate the object.
    res = Response[PatchResult].model_validate(resp.json())
    typer.echo(json.dumps(res.result, indent=2))


def _simple_call(ctx: typer.Context, method: str, selector: str) -> None:
    envelope = Request(
        id=str(uuid.uuid4()),
        method=method,
        params=SimpleSelectorParams(selector=selector).model_dump(),
    )
    resp = httpx.post(
        ctx.obj.get("gateway_url"),
        json=envelope.model_dump(mode="json"),
        timeout=30.0,
    )
    resp.raise_for_status()
    # Parse the already decoded JSON instead of using ``model_validate_json``
    res = Response[CountResult].model_validate(resp.json())
    typer.echo(json.dumps(res.result, indent=2))


@remote_task_app.command("pause")
def pause(
    ctx: typer.Context,
    selector: str = typer.Argument(..., help="Task ID or label selector"),
) -> None:
    """Pause one task or all tasks matching a label."""
    _simple_call(ctx, TASK_PAUSE, selector)


@remote_task_app.command("resume")
def resume(
    ctx: typer.Context,
    selector: str = typer.Argument(..., help="Task ID or label selector"),
) -> None:
    """Resume a paused task or label set."""
    _simple_call(ctx, TASK_RESUME, selector)


@remote_task_app.command("cancel")
def cancel(
    ctx: typer.Context,
    selector: str = typer.Argument(..., help="Task ID or label selector"),
) -> None:
    """Cancel a task or label set."""
    _simple_call(ctx, TASK_CANCEL, selector)


@remote_task_app.command("retry")
def retry(
    ctx: typer.Context,
    selector: str = typer.Argument(..., help="Task ID or label selector"),
) -> None:
    """Retry a task or label set."""
    _simple_call(ctx, TASK_RETRY, selector)


@remote_task_app.command("retry-from")
def retry_from(
    ctx: typer.Context,
    selector: str = typer.Argument(..., help="Task ID or label selector"),
) -> None:
    """Retry a task and its descendants."""
    _simple_call(ctx, TASK_RETRY_FROM, selector)
