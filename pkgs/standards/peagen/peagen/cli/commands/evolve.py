"""CLI for the evolve workflow."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

from peagen.cli.rpc_utils import rpc_post
from peagen.protocols.methods.task import SubmitResult, GetParams, GetResult
import typer
from functools import partial

from peagen.handlers.evolve_handler import evolve_handler
from peagen.orm.status import Status
from peagen.core.validate_core import validate_evolve_spec
from peagen.protocols import TASK_SUBMIT, TASK_GET
from peagen.cli.task_builder import _build_task as _generic_build_task

local_evolve_app = typer.Typer(help="Expand evolve spec and run mutate tasks")
remote_evolve_app = typer.Typer(help="Expand evolve spec and run mutate tasks")


_build_task = partial(_generic_build_task, "evolve")


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
    reply = rpc_post(
        ctx.obj.get("gateway_url"),
        TASK_SUBMIT,
        task.model_dump(mode="json"),
        result_model=SubmitResult,
    )
    if reply.error:
        typer.secho(
            f"Remote error {reply.error.code}: {reply.error.message}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)
    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
    if reply.result:
        typer.echo(json.dumps(reply.result.model_dump(), indent=2))
    if watch:

        def _rpc_call() -> GetResult:
            res = rpc_post(
                ctx.obj.get("gateway_url"),
                TASK_GET,
                GetParams(taskId=task.id).model_dump(),
                result_model=GetResult,
            )
            return res.result  # type: ignore[return-value]

        import time

        while True:
            task_reply = _rpc_call()
            typer.echo(json.dumps(task_reply, indent=2))
            if Status.is_terminal(task_reply["status"]):
                break
            time.sleep(interval)
