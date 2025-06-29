"""
CLI wrapper for querying asynchronous tasks.
"""

from __future__ import annotations

import json
import time

import typer

from peagen.transport import (
    TASK_GET,
    TASK_PATCH,
    TASK_PAUSE,
    TASK_RESUME,
    TASK_CANCEL,
    TASK_RETRY,
    TASK_RETRY_FROM,
)
from peagen.transport.json_rpcschemas.task import (
    GetParams,
    GetResult,
    PatchParams,
    PatchResult,
    SimpleSelectorParams,
    CountResult,
)
from peagen.cli.rpc_utils import rpc_post

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

    def _rpc_call() -> GetResult:
        res = rpc_post(
            ctx.obj.get("gateway_url"),
            TASK_GET,
            GetParams(taskId=task_id).model_dump(),
            result_model=GetResult,
        )
        return res.result  # type: ignore[return-value]

    while True:
        reply = _rpc_call()
        typer.echo(json.dumps(reply.model_dump(), indent=2))

        if not watch or Status.is_terminal(reply.status):
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
    res = rpc_post(
        ctx.obj.get("gateway_url"),
        TASK_PATCH,
        PatchParams(taskId=task_id, changes=payload).model_dump(),
        result_model=PatchResult,
    )
    typer.echo(json.dumps(res.result, indent=2))


def _simple_call(ctx: typer.Context, method: str, selector: str) -> None:
    res = rpc_post(
        ctx.obj.get("gateway_url"),
        method,
        SimpleSelectorParams(selector=selector).model_dump(),
        result_model=CountResult,
    )
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
