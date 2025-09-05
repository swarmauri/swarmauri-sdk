from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import List

import typer
from peagen.handlers.analysis_handler import analysis_handler
from peagen.cli.task_helpers import build_task, submit_task

local_analysis_app = typer.Typer(help="Aggregate run evaluation results.")
remote_analysis_app = typer.Typer(help="Aggregate run evaluation results.")


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
    task = build_task("analysis", args, pool=ctx.obj.get("pool", "default"))
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
    task = build_task("analysis", args, pool=ctx.obj.get("pool", "default"))
    reply = submit_task(ctx.obj["rpc"], task)
    if "error" in reply:
        typer.secho(
            f"Remote error {reply['error']['code']}: {reply['error']['message']}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)
    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
    typer.echo(json.dumps(reply.get("result", {}), indent=2))
