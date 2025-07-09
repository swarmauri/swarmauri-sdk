"""
peagen.handlers.analysis_handler
────────────────────────────────
Run-directory analysis executed by a worker.

Input : TaskRead  – AutoAPI schema for the `Task` table
Output: dict      – JSON-serialisable result from `analyze_runs`
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from autoapi.v2 import AutoAPI
from peagen.orm  import Task

from peagen._utils                import maybe_clone_repo
from peagen._utils.config_loader  import resolve_cfg
from peagen.core.analysis_core    import analyze_runs
from peagen.plugins               import PluginManager
from peagen.plugins.vcs           import pea_ref

from .repo_utils import fetch_repo, cleanup_repo

# ───────────────────────── schema handle ──────────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")      # ← includes `args` field


# ───────────────────────── helper: checkout repo ──────────────────────
def _checkout_repo(repo: Optional[str], ref: str) -> Tuple[Optional[Path], Optional[str]]:
    """Return (tmp_dir, prev_cwd) when *repo* is provided, else (None, None)."""
    if repo is None:
        return None, None
    return fetch_repo(repo, ref)                 # util in repo_utils


# ─────────────────────────── main coroutine ───────────────────────────
async def analysis_handler(task: TaskRead) -> Dict[str, Any]:
    """
    task.args MUST contain
    ----------------------
    {
        "run_dirs"  : ["out/run-001", ...],   # required, relative to repo root
        "spec_name" : "analysis",            # optional
        "repo"      : "<git url>",           # optional (local path if absent)
        "ref"       : "HEAD"                 # optional, defaults to HEAD
    }
    """
    args: Dict[str, Any] = task.args or {}

    # ─── extract & validate primary parameters ────────────────────────
    run_dirs     = [Path(p) for p in args.get("run_dirs", [])]
    if not run_dirs:
        raise ValueError("analysis_handler: 'run_dirs' must be non-empty")

    spec_name    = args.get("spec_name", "analysis")
    repo_url     = args.get("repo")          # may be None (local analysis)
    ref          = args.get("ref", "HEAD")

    # ─── optional checkout of remote repo ─────────────────────────────
    tmp_dir, prev_cwd = _checkout_repo(repo_url, ref)

    with maybe_clone_repo(repo_url, ref):
        result: Dict[str, Any] = analyze_runs(run_dirs, spec_name=spec_name)

    # ─── optional VCS integration (commit / branch push) ──────────────
    cfg = resolve_cfg()
    pm  = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:                             # plugin may be absent
        vcs = None

    if vcs and result.get("results_file"):
        analysis_branch = pea_ref("analysis", spec_name)
        vcs.create_branch(analysis_branch, "HEAD", checkout=True)

        # ensure run branches are merged (ours strategy)
        for rd in run_dirs:
            run_branch = pea_ref("run", rd.name)
            vcs.merge_ours(run_branch, f"merge {run_branch}")

        repo_root  = Path(vcs.repo.working_tree_dir)
        rel_path   = Path(result["results_file"]).resolve().relative_to(repo_root)
        commit_sha = vcs.commit([str(rel_path)], f"analysis {spec_name}")
        vcs.switch("HEAD")
        vcs.push(analysis_branch)

        result.update(
            commit=commit_sha,
            analysis_branch=analysis_branch,
        )

    # ─── cleanup checkout (if any) ────────────────────────────────────
    if repo_url:
        cleanup_repo(tmp_dir, prev_cwd)

    return result
