"""Evaluation command for Peagen."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from peagen.cli_common import PathOrURI, temp_workspace, load_peagen_toml
from peagen.plugin_registry import registry
from peagen.eval import DefaultEvaluatorPool
from swarmauri_standard.programs.Program import Program


eval_app = typer.Typer(help="Evaluate programs using an EvaluatorPool.")


@eval_app.command("eval")
def eval_cmd(
    workspace_uri: PathOrURI = typer.Argument(..., help="Workspace path or URI"),
    program_glob: str = typer.Argument("**/*.prog", help="Program glob pattern"),
    pool: Optional[str] = typer.Option(None, "--pool", "-p"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", exists=True),
    max_workers: int = typer.Option(10, "--max-workers"),
    async_: bool = typer.Option(False, "--async/--no-async"),
    out: Optional[Path] = typer.Option(None, "--out"),
    json_out: bool = typer.Option(False, "--json"),
    strict: bool = typer.Option(False, "--strict"),
    skip_failed: bool = typer.Option(False, "--skip-failed"),
):
    """Run evaluations and write an eval manifest."""

    cfg = load_peagen_toml(Path(workspace_uri))
    eval_cfg = cfg.get("evaluation", {})

    pool_ref = pool or eval_cfg.get("pool")
    if pool_ref:
        if pool_ref in registry.get("evaluator_pools", {}):
            PoolCls = registry["evaluator_pools"][pool_ref]
        else:
            mod_name, cls_name = pool_ref.rsplit(".", 1)
            PoolCls = getattr(__import__(mod_name, fromlist=[cls_name]), cls_name)
    else:
        PoolCls = DefaultEvaluatorPool

    pool_inst = PoolCls()
    pool_inst.initialize()

    workspace_path = Path(workspace_uri)
    if "://" in str(workspace_uri):
        with temp_workspace():
            # Reuse program.fetch helpers
            pass  # Placeholder for remote fetch logic
    programs = []
    for prog_path in workspace_path.glob(program_glob):
        if prog_path.is_file():
            programs.append(Program.from_workspace(prog_path.parent))

    results = pool_inst.evaluate_programs(programs)

    manifest = {
        "schemaVersion": "1.0.0",
        "evaluators": list(pool_inst.get_evaluator_names()),
        "results": [
            {
                "program_path": p,
                "score": r.score,
                "metadata": r.metadata,
            }
            for p, r in zip(
                [str(p) for p in workspace_path.glob(program_glob)], results
            )
        ],
    }

    if json_out:
        typer.echo(json.dumps(manifest, indent=2))
    else:
        out_dir = out or workspace_path / ".peagen"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "eval_manifest.json"
        out_file.write_text(json.dumps(manifest, indent=2))
        typer.echo(str(out_file))

    if strict and any(r.score == 0 for r in results):
        raise typer.Exit(3)
