"""CLI for the evolve workflow."""
from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from typing import Optional

import httpx
import typer

from peagen.handlers.evolve_handler import evolve_handler
from peagen.models import Task

local_evolve_app = typer.Typer(help="Expand evolve spec and run mutate tasks")
remote_evolve_app = typer.Typer(help="Expand evolve spec and run mutate tasks")


def _build_task(args: dict) -> Task:
    return Task(
        id=str(uuid.uuid4()),
        pool="default",
        status=Status.waiting,
        payload={"action": "evolve", "args": args},
    )


@local_evolve_app.command("evolve")
def run(
    ctx: typer.Context,
    spec: Path = typer.Argument(..., exists=True),
    json_out: bool = typer.Option(False, "--json"),
    out: Optional[Path] = typer.Option(None, "--out", help="Write results to file"),
):
    args = {"evolve_spec": str(spec)}
    task = _build_task(args)
    result = asyncio.run(evolve_handler(task))
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        out_file = out or spec.with_suffix(".evolve_result.json")
        out_file.write_text(json.dumps(result, indent=2))
        typer.echo(str(out_file))


@remote_evolve_app.command("evolve")
def submit(
    ctx: typer.Context,
    spec: Path = typer.Argument(..., exists=True),
    watch: bool = typer.Option(False, "--watch", "-w", help="Poll until finished"),
    interval: float = typer.Option(2.0, "--interval", "-i", help="Seconds between polls"),
):
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
    if reply.get("result"):
        typer.echo(json.dumps(reply["result"], indent=2))
    if watch:
        def _rpc_call() -> dict:
            req = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "Task.get",
                "params": {"taskId": task.id},
            }
            res = httpx.post(ctx.obj.get("gateway_url"), json=req, timeout=30.0).json()
            return res["result"]

        import time

        while True:
            task_reply = _rpc_call()
            typer.echo(json.dumps(task_reply, indent=2))
            if task_reply["status"] in {"finished", "failed"}:
                break
            time.sleep(interval)
