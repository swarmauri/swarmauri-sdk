# peagen/core/eval_core.py
"""
Pure business-logic for evaluating programs with an EvaluatorPool.

Functions
---------
evaluate_workspace()  – orchestrates one evaluation run and returns a report
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from importlib import import_module

from peagen.common import PathOrURI, temp_workspace
from peagen._utils.config_loader import load_peagen_toml
from peagen.plugin_manager import resolve_plugin_spec
from peagen.plugins.evaluator_pools.default import DefaultEvaluatorPool
from swarmauri_standard.programs.Program import Program


# ───────────────────────── helper: pool resolution ──────────────────────────
def _build_pool(pool_ref: Optional[str], eval_cfg: Dict[str, Any]):
    """
    Return an *initialised* EvaluatorPool instance based on config.
    """
    choice = pool_ref or eval_cfg.get("pool")
    if choice:
        PoolCls = resolve_plugin_spec("evaluator_pools", choice)
    else:
        PoolCls = DefaultEvaluatorPool

    pool = PoolCls()
    pool.initialize()
    return pool


# ─────────────── helper: evaluator registration/update ─────────────────────
def _register_evaluators(pool, evaluators_cfg: Dict[str, Any]):
    """
    Attach evaluators described in *evaluators_cfg* to *pool*.
    Support both string and dict forms from .peagen.toml.
    """
    for name, spec in evaluators_cfg.items():
        if name == "default_evaluator":
            continue
        # ------------------------------------------------------------------ #
        # 1) Instantiate or locate evaluator
        # ------------------------------------------------------------------ #
        if isinstance(spec, str):
            if "." in spec or ":" in spec:
                mod, cls = spec.split(":", 1) if ":" in spec else spec.rsplit(".", 1)
                EvalCls = getattr(import_module(mod), cls)
            else:
                EvalCls = resolve_plugin_spec("evaluators", spec)
            evaluator = EvalCls()
        elif isinstance(spec, dict):
            if "cls" in spec:
                mod, cls = (
                    spec["cls"].split(":", 1)
                    if ":" in spec["cls"]
                    else spec["cls"].rsplit(".", 1)
                )
                EvalCls = getattr(import_module(mod), cls)
            else:
                EvalCls = resolve_plugin_spec("evaluators", name)

            args = dict(spec.get("args", {}))
            args.update({k: v for k, v in spec.items() if k not in {"cls", "args"}})
            evaluator = EvalCls(**args)
        else:
            raise ValueError(f"Invalid evaluator specification for '{name}': {spec}")

        # ------------------------------------------------------------------ #
        # 2) Add or update on the pool
        # ------------------------------------------------------------------ #
        existing = pool.get_evaluator(name)
        if existing is None:
            pool.add_evaluator(evaluator, name=name)
        else:
            if isinstance(spec, dict):  # re-configure existing instance
                args = dict(spec.get("args", {}))
                args.update({k: v for k, v in spec.items() if k not in {"cls", "args"}})
                if callable(getattr(existing, "configure", None)):
                    existing.configure(args)
                else:
                    for k, v in args.items():
                        setattr(existing, k, v)


# ─────────────── helper: workspace program discovery ───────────────────────
def _collect_programs(
    workspace_uri: str, pattern: str
) -> Tuple[List[Path], List[Program]]:
    """
    Return (program_paths, Program instances) for *workspace_uri*.
    Remote URIs are fetched into a temp dir via program.fetch helpers.
    """
    if "://" in workspace_uri:
        # NOTE: rely on fetch_core to materialise remote workspace first
        from peagen.core.fetch_core import fetch_single  # local import to avoid cycle

        with temp_workspace() as tmp_dir:
            fetch_single(workspace_uri, dest_root=tmp_dir)
            workspace_path = tmp_dir
    else:
        workspace_path = Path(PathOrURI(workspace_uri))

    paths: List[Path] = []
    programs: List[Program] = []
    for p in workspace_path.glob(pattern):
        if p.is_file():
            paths.append(p)
            programs.append(Program.from_workspace(p.parent))

    return paths, programs


# ───────────────────────────── public API ───────────────────────────────────
def evaluate_workspace(
    *,
    workspace_uri: str,
    program_glob: str = "**/*.*",
    pool_ref: Optional[str] = None,
    cfg_path: Optional[Path] = None,
    async_eval: bool = False,
    skip_failed: bool = False,
) -> Dict[str, Any]:
    """
    Evaluate programs in *workspace_uri* according to configuration.

    Returns a JSON-serialisable report (no I/O side-effects).
    """
    # 1) resolve configuration file (.peagen.toml) -------------------------
    if cfg_path is None:
        ws_cfg = Path(workspace_uri) / ".peagen.toml"
        cwd_cfg = Path.cwd() / ".peagen.toml"
        cfg_path = ws_cfg if ws_cfg.exists() else cwd_cfg
        if not cfg_path.exists():
            raise FileNotFoundError(
                "No .peagen.toml configuration found – supply cfg_path explicitly."
            )

    cfg = load_peagen_toml(cfg_path)
    eval_cfg: Dict[str, Any] = cfg.get("evaluation", {})

    # 2) build evaluator pool + register evaluators ------------------------
    pool = _build_pool(pool_ref, eval_cfg)
    _register_evaluators(pool, eval_cfg.get("evaluators", {}))

    # 3) collect program files --------------------------------------------
    prog_paths, progs = _collect_programs(workspace_uri, program_glob)

    # 4) run evaluation ----------------------------------------------------
    if async_eval:
        results = asyncio.run(pool.evaluate_async(progs))
    else:
        results = pool.evaluate(progs)

    # 5) optional filtering ------------------------------------------------
    paired = (
        [(pp, rr) for pp, rr in zip(prog_paths, results) if rr.score > 0]
        if skip_failed
        else list(zip(prog_paths, results))
    )

    # 6) build report ----------------------------------------------------
    report = {
        "schemaVersion": "1.0.0",
        "evaluators": pool.get_evaluator_names(),
        "results": [
            {
                "program_path": str(pp),
                "score": rr.score,
                "metadata": rr.metadata,
            }
            for pp, rr in paired
        ],
    }
    return report
