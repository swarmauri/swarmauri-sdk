from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from typing import List

import httpx
import typer
from peagen.errors import GitRemoteMissingError

from peagen.handlers.analysis_handler import analysis_handler
from peagen.models import Status, Task

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
local_analysis_app = typer.Typer(help="Aggregate run evaluation results.")
remote_analysis_app = typer.Typer(help="Aggregate run evaluation results.")


def _build_task(args: dict) -> Task:
    return Task(
        id=str(uuid.uuid4()),
        pool="default",
        status=Status.waiting,
        payload={"action": "analysis", "args": args},
    )


@local_analysis_app.command("analysis")
def run(
    ctx: typer.Context,
    run_dirs: List[Path] = typer.Argument(..., exists=True, dir_okay=True),
    spec_name: str = typer.Option(..., "--spec-name", "-s"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    args = {"run_dirs": [str(p) for p in run_dirs], "spec_name": spec_name}
    task = _build_task(args)
    result = asyncio.run(analysis_handler(task))
    typer.echo(
        json.dumps(result, indent=2) if json_out else json.dumps(result, indent=2)
    )


@remote_analysis_app.command("analysis")
def submit(
    ctx: typer.Context,
    run_dirs: List[Path] = typer.Argument(..., exists=True, dir_okay=True),
    spec_name: str = typer.Option(..., "--spec-name", "-s"),
) -> None:
    try:
        from peagen._utils.git_utils import require_origin

        require_origin(run_dirs[0])
    except GitRemoteMissingError as exc:
        typer.secho(f"[ERROR] {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    args = {"run_dirs": [str(p) for p in run_dirs], "spec_name": spec_name}
    task = _build_task(args)
    rpc_req = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"taskId": task.id, "pool": task.pool, "payload": task.payload},
    }
    with httpx.Client(timeout=30.0) as client:
        reply = client.post(ctx.obj.get("gateway_url"), json=rpc_req).json()
    if "error" in reply:
        typer.secho(
            f"Remote error {reply['error']['code']}: {reply['error']['message']}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)
    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
    typer.echo(json.dumps(reply.get("result", {}), indent=2))
