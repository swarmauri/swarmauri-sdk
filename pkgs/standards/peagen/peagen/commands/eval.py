"""Evaluation command for Peagen."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer

from importlib import import_module

from peagen.cli_common import PathOrURI, temp_workspace, load_peagen_toml
from peagen.plugin_registry import registry
from peagen.eval import DefaultEvaluatorPool
from swarmauri_standard.programs.Program import Program


eval_app = typer.Typer(help="Evaluate programs using an EvaluatorPool.")


# ---------------------------------------------------------------------------

@eval_app.command("eval")
def eval_cmd(
    workspace_uri: str = typer.Argument(..., help="Workspace path or URI"),
    program_glob: str = typer.Argument("**/*.*", help="Program glob pattern"),
    pool: Optional[str] = typer.Option(None, "--pool", "-p"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", exists=True),
    max_workers: int = typer.Option(10, "--max-workers"),  # reserved for future
    async_: bool = typer.Option(False, "--async/--no-async"),
    out: Optional[Path] = typer.Option(None, "--out"),
    json_out: bool = typer.Option(False, "--json"),
    strict: bool = typer.Option(False, "--strict"),
    skip_failed: bool = typer.Option(False, "--skip-failed"),
):
    """
    Run evaluations over programs in *workspace_uri* and emit an eval-manifest.

    Resolution order for the configuration file when --config/-c is **not** given:
    \n\n
        1. <workspace_uri>/.peagen.toml\n
        2. <current working directory>/.peagen.toml
    """

    # ── locate .peagen.toml ----------------------------------------------------
    if config is not None:
        cfg_path = config
    else:
        ws_cfg  = Path(workspace_uri) / ".peagen.toml"
        cwd_cfg = Path.cwd() / ".peagen.toml"
        cfg_path = ws_cfg if ws_cfg.exists() else cwd_cfg

    if not cfg_path.exists():
        raise typer.BadParameter(
            f"No .peagen.toml found – supply one with --config or place it in\n"
            f"  {ws_cfg}\n  {cwd_cfg}"
        )

    cfg       = load_peagen_toml(cfg_path)
    eval_cfg  = cfg.get("evaluation", {})

    # ── resolve EvaluatorPool --------------------------------------------------
    pool_ref = pool or eval_cfg.get("pool")
    if pool_ref:
        if pool_ref in registry.get("evaluator_pools", {}):
            PoolCls = registry["evaluator_pools"][pool_ref]
        else:                                   # dotted-path or module:Class
            mod_name, cls_name = (
                pool_ref.split(":", 1) if ":" in pool_ref else pool_ref.rsplit(".", 1)
            )
            PoolCls = getattr(import_module(mod_name), cls_name)
    else:
        PoolCls = DefaultEvaluatorPool

    pool_inst = PoolCls()
    pool_inst.initialize()                      # thread-pool etc.

    # ── register evaluators ----------------------------------------------------
    evaluators_cfg = eval_cfg.get("evaluators", {})
    for name, spec in evaluators_cfg.items():
        if isinstance(spec, str):
            mod, cls = (spec.split(":", 1) if ":" in spec else spec.rsplit(".", 1))
            EvalCls = getattr(import_module(mod), cls)
            evaluator = EvalCls()
        elif isinstance(spec, dict) and "cls" in spec:
            mod, cls = (
                spec["cls"].split(":", 1)
                if ":" in spec["cls"]
                else spec["cls"].rsplit(".", 1)
            )
            EvalCls = getattr(import_module(mod), cls)
            evaluator = EvalCls(**spec.get("args", {}))
        else:
            raise ValueError(f"Invalid evaluator spec for '{name}': {spec}")
        pool_inst.add_evaluator(evaluator, name=name)

    # ── collect programs -------------------------------------------------------
    workspace_path = Path(PathOrURI(workspace_uri))
    if "://" in workspace_uri:
        # TODO: remote fetch logic via program.fetch helpers
        with temp_workspace():
            ...

    program_paths: List[Path] = []
    programs      : List[Program] = []
    for p in workspace_path.glob(program_glob):
        if p.is_file():
            program_paths.append(p)
            programs.append(Program.from_workspace(p.parent))

    # ── run evaluation ---------------------------------------------------------
    if async_:
        results = asyncio.run(pool_inst.evaluate_async(programs))
    else:
        results = pool_inst.evaluate(programs)

    # optionally skip programs that totally failed
    if skip_failed:
        paired = [(pp, rr) for pp, rr in zip(program_paths, results) if rr.score > 0]
    else:
        paired = list(zip(program_paths, results))

    # ── build manifest ---------------------------------------------------------
    manifest = {
        "schemaVersion": "1.0.0",
        "evaluators": pool_inst.get_evaluator_names(),
        "results": [
            {
                "program_path": str(pp),
                "score": rr.score,
                "metadata": rr.metadata,
            }
            for pp, rr in paired
        ],
    }

    # ── output -----------------------------------------------------------------
    if json_out:
        typer.echo(json.dumps(manifest, indent=2))
    else:
        out_dir  = out or workspace_path / ".peagen"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "eval_manifest.json"
        out_file.write_text(json.dumps(manifest, indent=2))
        typer.echo(str(out_file))

    # ── strict / CI gate -------------------------------------------------------
    if strict and any(r.score == 0 for _, r in paired):
        raise typer.Exit(3)