"""CLI for the mutate workflow."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

from peagen.cli.rpc_utils import rpc_post

import typer
from functools import partial

from peagen.handlers.mutate_handler import mutate_handler
from peagen.protocols import TASK_SUBMIT
from peagen.transport.json_rpcschemas.task import SubmitParams, SubmitResult
from peagen.cli.task_builder import _build_task as _generic_build_task

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
local_mutate_app = typer.Typer(help="Run the mutate workflow")
remote_mutate_app = typer.Typer(help="Run the mutate workflow")


_build_task = partial(_generic_build_task, "mutate")


@local_mutate_app.command("mutate")
def run(
    ctx: typer.Context,
    workspace_uri: str = typer.Argument(..., help="Workspace path"),
    target_file: str = typer.Option(..., help="File to mutate"),
    import_path: str = typer.Option(..., help="Module import path"),
    entry_fn: str = typer.Option(..., help="Benchmark function"),
    profile_mod: Optional[str] = typer.Option(None, help="Profile helper module"),
    fitness: str = typer.Option(
        "peagen.plugins.evaluators.performance_evaluator:PerformanceEvaluator",
        "--fitness",
        help="Evaluator plugin reference",
    ),
    mutator: str = typer.Option(
        "default_mutator",
        "--mutator",
        help="Mutator plugin name",
    ),
    gens: int = typer.Option(1, help="Number of generations"),
    json_out: bool = typer.Option(
        False, "--json", help="Print results to stdout instead of a file"
    ),
    out: Optional[Path] = typer.Option(
        None, "--out", help="Write JSON results to this path"
    ),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
) -> None:
    """Run the mutate workflow locally."""
    args = {
        "workspace_uri": workspace_uri if not repo else f"git+{repo}@{ref}",
        "target_file": target_file,
        "import_path": import_path,
        "entry_fn": entry_fn,
        "profile_mod": profile_mod,
        "gens": gens,
        "evaluator_ref": fitness,
        "mutations": [{"kind": mutator}],
    }
    task = _build_task(args, ctx.obj.get("pool", "default"))
    result = asyncio.run(mutate_handler(task))

    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        out_file = out or Path(workspace_uri) / "mutate_result.json"
        out_file.write_text(json.dumps(result, indent=2))
        typer.echo(str(out_file))


@remote_mutate_app.command("mutate")
def submit(
    ctx: typer.Context,
    workspace_uri: str = typer.Argument(..., help="Workspace path"),
    target_file: str = typer.Option(..., help="File to mutate"),
    import_path: str = typer.Option(..., help="Module import path"),
    entry_fn: str = typer.Option(..., help="Benchmark function"),
    profile_mod: Optional[str] = typer.Option(None, help="Profile helper module"),
    fitness: str = typer.Option(
        "peagen.plugins.evaluators.performance_evaluator:PerformanceEvaluator",
        "--fitness",
        help="Evaluator plugin reference",
    ),
    mutator: str = typer.Option(
        "default_mutator",
        "--mutator",
        help="Mutator plugin name",
    ),
    gens: int = typer.Option(1, help="Number of generations"),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
) -> None:
    """Submit a mutate task to the gateway."""
    args = {
        "workspace_uri": workspace_uri if not repo else f"git+{repo}@{ref}",
        "target_file": target_file,
        "import_path": import_path,
        "entry_fn": entry_fn,
        "profile_mod": profile_mod,
        "gens": gens,
        "evaluator_ref": fitness,
        "mutations": [{"kind": mutator}],
    }
    task = _build_task(args, ctx.obj.get("pool", "default"))

    reply = rpc_post(
        ctx.obj.get("gateway_url"),
        TASK_SUBMIT,
        SubmitParams(task=task).model_dump(),
        result_model=SubmitResult,
    )

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
