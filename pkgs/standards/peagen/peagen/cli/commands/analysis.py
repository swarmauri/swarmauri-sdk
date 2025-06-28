from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import List

from peagen.cli.rpc_utils import rpc_post
import typer
from functools import partial

from peagen.handlers.analysis_handler import analysis_handler
from peagen.protocols import TASK_SUBMIT
from peagen.protocols.methods.task import SubmitParams, SubmitResult
from peagen.cli.task_builder import _build_task as _generic_build_task

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
local_analysis_app = typer.Typer(help="Aggregate run evaluation results.")
remote_analysis_app = typer.Typer(help="Aggregate run evaluation results.")


_build_task = partial(_generic_build_task, "analysis")


@local_analysis_app.command("analysis")
def run(
    ctx: typer.Context,
    run_dirs: List[Path] = typer.Argument(..., exists=True, dir_okay=True),
    spec_name: str = typer.Option(..., "--spec-name", "-s"),
    json_out: bool = typer.Option(False, "--json"),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
) -> None:
    args = {"run_dirs": [str(p) for p in run_dirs], "spec_name": spec_name}
    if repo:
        args.update({"repo": repo, "ref": ref})
    task = _build_task(args, ctx.obj.get("pool", "default"))
    result = asyncio.run(analysis_handler(task))
    typer.echo(
        json.dumps(result, indent=2) if json_out else json.dumps(result, indent=2)
    )


@remote_analysis_app.command("analysis")
def submit(
    ctx: typer.Context,
    run_dirs: List[Path] = typer.Argument(..., exists=True, dir_okay=True),
    spec_name: str = typer.Option(..., "--spec-name", "-s"),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
) -> None:
    args = {"run_dirs": [str(p) for p in run_dirs], "spec_name": spec_name}
    if repo:
        args.update({"repo": repo, "ref": ref})
    task = _build_task(args, ctx.obj.get("pool", "default"))
    reply = rpc_post(
        ctx.obj.get("gateway_url"),
        TASK_SUBMIT,
        SubmitParams(task=task).model_dump(),
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
    typer.echo(json.dumps(reply.result.model_dump() if reply.result else {}, indent=2))
