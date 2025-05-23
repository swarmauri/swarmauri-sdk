"""Run evaluator pools against a workspace."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Optional

import typer

from swarmauri_standard.programs.Program import Program


eval_app = typer.Typer(help="Evaluate a workspace using an evaluator pool.")


@eval_app.command("eval")
def eval_cmd(
    workspace: Path = typer.Argument(
        ..., exists=True, file_okay=False, resolve_path=True, readable=True,
        help="Path to the workspace directory to evaluate.",
    ),
    pool: str = typer.Option(
        ..., "--pool", "-p", help="Evaluator pool as 'module:Class'"
    ),
) -> None:
    """Instantiate *pool* and run evaluation on *workspace*."""

    mod, cls = pool.split(":", 1)
    module = importlib.import_module(mod)
    PoolCls = getattr(module, cls)
    pool_obj = PoolCls()
    pool_obj.initialize()
    try:
        program = Program.from_workspace(workspace)
        results = pool_obj.evaluate([program])
        typer.echo(json.dumps([{
            "score": r.score,
            "metadata": r.metadata,
        } for r in results], indent=2))
    finally:
        pool_obj.shutdown()

