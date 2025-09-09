"""
peagen.core.eval_core
=====================
Business logic for evaluating programs with an EvaluatorPool.

Public entry-point
------------------
evaluate_workspace() – orchestrates one evaluation run for a given
(repo, ref) and returns a JSON-serialisable report.

Key guarantees
--------------
* **Work-tree per run** – every invocation checks-out a dedicated work-tree
  at <ROOT_DIR>/worktrees/<repo-hash>/<ref>/<task>/<run>.
* **Concurrency-safe** – all Git writes are wrapped in ``repo_lock(repo)``.
* **No repository mutations** – artefacts remain in the ephemeral work-tree
  which is removed on exit.
"""

from __future__ import annotations

import asyncio
import hashlib
import shutil
import uuid
from contextlib import suppress
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from peagen._utils.config_loader import load_peagen_toml
from peagen.defaults import ROOT_DIR
from peagen.plugin_manager import resolve_plugin_spec
from peagen.plugins.evaluator_pools.default import DefaultEvaluatorPool
from peagen.core.git_repo_core import (
    repo_lock,
    open_repo,
    fetch_git_remote,
)
from swarmauri_standard.programs import Program


# ───────────────────────── helper: pool resolution ──────────────────────────
def _build_pool(pool_ref: Optional[str], eval_cfg: Dict[str, Any]):
    choice = pool_ref or eval_cfg.get("pool")
    PoolCls = (
        resolve_plugin_spec("evaluator_pools", choice)
        if choice
        else DefaultEvaluatorPool
    )
    pool = PoolCls()
    pool.initialize()
    return pool


# ─────────────── helper: evaluator registration/update ─────────────────────
def _register_evaluators(pool, evaluators_cfg: Dict[str, Any]):
    for name, spec in evaluators_cfg.items():
        if name == "default_evaluator":
            continue

        # 1) resolve implementation class -------------------------------
        if isinstance(spec, str):
            mod, cls = spec.split(":", 1) if ":" in spec else spec.rsplit(".", 1)
            EvalCls = (
                getattr(import_module(mod), cls)
                if "." in spec or ":" in spec
                else resolve_plugin_spec("evaluators", spec)
            )
            evaluator = EvalCls()
            kwargs: Dict[str, Any] = {}
        elif isinstance(spec, dict):
            cls_spec = spec.get("cls", name)
            mod, cls = (
                cls_spec.split(":", 1) if ":" in cls_spec else cls_spec.rsplit(".", 1)
            )
            EvalCls = getattr(import_module(mod), cls)
            kwargs = {
                **spec.get("args", {}),
                **{k: v for k, v in spec.items() if k not in {"cls", "args"}},
            }
            evaluator = EvalCls(**kwargs)
        else:
            raise ValueError(f"Invalid evaluator specification for '{name}': {spec}")

        # 2) register / reconfigure -------------------------------------
        existing = pool.get_evaluator(name)
        if existing is None:
            pool.add_evaluator(evaluator, name=name)
        elif isinstance(spec, dict) and callable(getattr(existing, "configure", None)):
            existing.configure(kwargs)  # type: ignore[arg-type]


# ───────────── helper: workspace program discovery (local only) ─────────────
def _collect_programs(
    workspace: Path, pattern: str
) -> Tuple[List[Path], List[Program]]:
    paths, programs = [], []
    for p in workspace.glob(pattern):
        if p.is_file():
            paths.append(p)
            programs.append(Program.from_workspace(p.parent))
    return paths, programs


# ──────────────────────── helper: work-tree path  ───────────────────────────
def _worktree_path(repo: str, ref: str, task: str = "eval") -> Path:
    """Deterministic path for the current work-tree."""
    repo_hash = hashlib.sha1(repo.encode()).hexdigest()[:12]
    run_id = uuid.uuid4().hex[:10]
    return (
        Path(ROOT_DIR).expanduser()
        / "worktrees"
        / repo_hash
        / ref.replace("/", "_")
        / task
        / run_id
    )


# ───────────────────────────── public API ───────────────────────────────────
def evaluate_workspace(
    *,
    repo: str,
    ref: str = "HEAD",
    program_glob: str = "**/*.*",
    pool_ref: Optional[str] = None,
    cfg_path: Optional[Path] = None,
    async_eval: bool = False,
    skip_failed: bool = False,
) -> Dict[str, Any]:
    """
    Evaluate programs at *repo*@*ref* and return a summary report.

    This function never mutates the repository: it fetches latest refs,
    materialises an isolated work-tree, runs the EvaluatorPool, then deletes
    the work-tree before returning.
    """

    # 1) establish mirror & work-tree ------------------------------------
    mirror_base = Path(ROOT_DIR).expanduser() / "mirrors"
    mirror_base.mkdir(parents=True, exist_ok=True)

    mirror_path = mirror_base / hashlib.sha1(repo.encode()).hexdigest()[:12]
    worktree_path = _worktree_path(repo, ref)

    with repo_lock(repo):
        git_repo = open_repo(mirror_path, remote_url=repo)
        fetch_git_remote(git_repo)

        # ensure fresh work-tree
        if worktree_path.exists():
            shutil.rmtree(worktree_path, ignore_errors=True)
        git_repo.git.worktree("add", str(worktree_path), ref)

    # 2) locate .peagen.toml --------------------------------------------
    if cfg_path is None:
        ws_cfg = worktree_path / ".peagen.toml"
        cwd_cfg = Path.cwd() / ".peagen.toml"
        cfg_path = ws_cfg if ws_cfg.exists() else cwd_cfg
        if not cfg_path.exists():
            with suppress(Exception):
                shutil.rmtree(worktree_path, ignore_errors=True)
            raise FileNotFoundError(
                "No .peagen.toml configuration found – supply cfg_path explicitly."
            )

    cfg = load_peagen_toml(cfg_path)
    eval_cfg = cfg.get("evaluation", {})

    # 3) build evaluator pool & register evaluators ---------------------
    pool = _build_pool(pool_ref, eval_cfg)
    _register_evaluators(pool, eval_cfg.get("evaluators", {}))

    # 4) discover programs ----------------------------------------------
    prog_paths, programs = _collect_programs(worktree_path, program_glob)

    # 5) run evaluation --------------------------------------------------
    results = (
        asyncio.run(pool.evaluate_async(programs))
        if async_eval
        else pool.evaluate(programs)
    )

    # 6) optionally filter failures -------------------------------------
    paired = [
        (p, r) for p, r in zip(prog_paths, results) if (r.score > 0 or not skip_failed)
    ]

    # 7) synthesize report ----------------------------------------------
    report = {
        "schemaVersion": "1.0.0",
        "evaluators": pool.get_evaluator_names(),
        "results": [
            {"program_path": str(p), "score": r.score, "metadata": r.metadata}
            for p, r in paired
        ],
    }

    # 8) cleanup work-tree ----------------------------------------------
    with suppress(Exception):
        # remove work-tree from Git *and* delete files
        try:
            git_repo.git.worktree("remove", "--force", str(worktree_path))
        except Exception:
            pass
        shutil.rmtree(worktree_path, ignore_errors=True)

    return report
