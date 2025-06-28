"""CLI for the evolve workflow."""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
import typer

from peagen.handlers.evolve_handler import evolve_handler
from peagen.orm.status import Status
from peagen.core.validate_core import validate_evolve_spec
from peagen.defaults import TASK_SUBMIT
from peagen.schemas import TaskCreate
from peagen.transport import RPCRequest, RPCResponse

local_evolve_app = typer.Typer(help="Expand evolve spec and run mutate tasks")
remote_evolve_app = typer.Typer(help="Expand evolve spec and run mutate tasks")


def _build_task(args: dict, pool: str = "default") -> TaskCreate:
    return TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool=pool,
        payload={"action": "evolve", "args": args},
        status=Status.queued,
        note="",
        spec_hash="dummy",
        last_modified=datetime.utcnow(),
    )


@local_evolve_app.command("evolve")
def run(
    ctx: typer.Context,
    spec: Path = typer.Argument(..., exists=True),
    json_out: bool = typer.Option(False, "--json"),
    out: Optional[Path] = typer.Option(None, "--out", help="Write results to file"),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    result = validate_evolve_spec(spec)
    if not result["ok"]:
        for err in result["errors"]:
            typer.secho(err, fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    def _git_root(path: Path) -> Path:
        for p in [path] + list(path.parents):
            if (p / ".git").exists():
                return p
        return path

    root = _git_root(Path.cwd())

    def _canonical(p: Path) -> str:
        try:
            return str(p.resolve().relative_to(root))
        except ValueError:
            return str(p.resolve())

    args = {"evolve_spec": _canonical(spec)}
    if repo:
        args.update({"repo": repo, "ref": ref})
    task = _build_task(args, ctx.obj.get("pool", "default"))
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
    interval: float = typer.Option(
        2.0, "--interval", "-i", help="Seconds between polls"
    ),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    result = validate_evolve_spec(spec)
    if not result["ok"]:
        for err in result["errors"]:
            typer.secho(err, fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    def _git_root(path: Path) -> Path:
        for p in [path] + list(path.parents):
            if (p / ".git").exists():
                return p
        return path

    root = _git_root(Path.cwd())

    def _canonical(p: Path) -> str:
        try:
            return str(p.resolve().relative_to(root))
        except ValueError:
            return str(p.resolve())

    args = {"evolve_spec": _canonical(spec)}
    if repo:
        args.update({"repo": repo, "ref": ref})
    task = _build_task(args, ctx.obj.get("pool", "default"))
    rpc_req = RPCRequest(method=TASK_SUBMIT, params=task.model_dump(mode="json"))
    with httpx.Client(timeout=30.0) as client:
        reply = client.post(
            ctx.obj.get("gateway_url"), json=rpc_req.model_dump()
        ).json()
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
            req = RPCRequest(
                id=str(uuid.uuid4()),
                method="Task.get",
                params={"taskId": task.id},
            )
            res = httpx.post(
                ctx.obj.get("gateway_url"), json=req.model_dump(), timeout=30.0
            ).json()
            return RPCResponse.model_validate(res).result

        import time

        while True:
            task_reply = _rpc_call()
            typer.echo(json.dumps(task_reply, indent=2))
            if Status.is_terminal(task_reply["status"]):
                break
            time.sleep(interval)
