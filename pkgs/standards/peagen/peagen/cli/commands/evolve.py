"""CLI for the evolve workflow."""
from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path

import httpx
import typer

from peagen.handlers.evolve_handler import evolve_handler
from peagen.models import Status, Task

local_evolve_app = typer.Typer(help="Expand evolve spec and run mutate tasks")
remote_evolve_app = typer.Typer(help="Expand evolve spec and run mutate tasks")


def _build_task(args: dict) -> Task:
    return Task(
        id=str(uuid.uuid4()),
        pool="default",
        action="evolve",
        status=Status.waiting,
        payload={"action": "evolve", "args": args},
    )


@local_evolve_app.command("evolve")
def run(ctx: typer.Context, spec: Path = typer.Argument(..., exists=True), json_out: bool = typer.Option(False, "--json")):
    args = {"evolve_spec": str(spec)}
    task = _build_task(args)
    result = asyncio.run(evolve_handler(task))
    typer.echo(json.dumps(result, indent=2) if json_out else json.dumps(result, indent=2))


@remote_evolve_app.command("evolve")
def submit(ctx: typer.Context, spec: Path = typer.Argument(..., exists=True)):
    args = {"evolve_spec": str(spec)}
    task = _build_task(args)
    rpc_req = {
        "jsonrpc": "2.0",
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
