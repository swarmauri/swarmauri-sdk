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

from autoapi_client import AutoAPIClient
from autoapi.v2 import AutoAPI
from peagen.orm.task import TaskModel

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

        if not watch or Status.is_terminal(reply.status):
            break
        time.sleep(interval)


@remote_task_app.command("patch")
def patch_task(
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="UUID of the task to update"),
    changes: str = typer.Argument(..., help="JSON dict of fields to modify"),
):
    """PATCH a Task via JSON-RPC using dynamic schemas."""

    # auto-discover the exact schemas AutoAPI generated
    SUpdate = AutoAPI.get_schema(TaskModel, "update")   # body (id excluded)
    SRead   = AutoAPI.get_schema(TaskModel, "read")     # success result

    # validate & coerce the payload
    changes_obj = SUpdate.model_validate(json.loads(changes))

    # build the RPC params: primary key + validated changes
    params = {"id": task_id, **changes_obj.model_dump(exclude_unset=True)}

    with AutoAPIClient(ctx.obj["gateway_url"]) as rpc:
        result = rpc.call(
            "Tasks.update",                    # method string inline
            params=params,
            out_schema=SRead,
        )
    typer.echo(json.dumps(result.model_dump(), indent=2))