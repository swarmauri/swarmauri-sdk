"""
peagen.handlers.analysis_handler
────────────────────────────────
Run-directory analysis worker.

Key changes
-----------
* Requires caller to pass an **existing work-tree** via `task.args["worktree"]`.
  No cloning, no `maybe_clone_repo`, no `repo_utils`.
* `run_dirs` may be absolute or *relative to the supplied work-tree*.
* No storage-adapter logic.
"""

from __future__ import annotations

import os
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict, List

from tigrbl.v3 import get_schema
from peagen.orm import Task
from peagen.core.analysis_core import analyze_runs
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import GitVCS, pea_ref

# ───────────────────────── schema handle ────────────────────────────
TaskRead = get_schema(Task, "read")


# ─────────────────────────‍ main coroutine ──────────────────────────
async def analysis_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Expected ``task.args``::

        {
            "run_dirs":  ["out/run-001", ...],  # list of run directories
            "worktree":  "<abs path>",          # required – task work-tree
            "spec_name": "analysis",            # optional
        }
    """
    args: Dict[str, Any] = task.args or {}

    worktree = Path(args["worktree"]).expanduser().resolve()
    if not worktree.exists():
        raise FileNotFoundError(f"worktree not found: {worktree}")

    # resolve run directories
    run_dirs_arg: List[str] = args.get("run_dirs", [])
    if not run_dirs_arg:
        raise ValueError("'run_dirs' must be a non-empty list")

    run_dirs: List[Path] = [
        (worktree / p).resolve() if not Path(p).is_absolute() else Path(p).resolve()
        for p in run_dirs_arg
    ]

    spec_name = args.get("spec_name", "analysis")

    # ─── perform analysis ────────────────────────────────────────────
    result = analyze_runs(run_dirs, spec_name=spec_name)

    # ─── optional VCS integration ────────────────────────────────────
    cfg_path = worktree / ".peagen.toml"
    cfg = resolve_cfg(toml_path=str(cfg_path) if cfg_path.exists() else None)
    pm = PluginManager(cfg)

    with suppress(Exception):
        vcs: GitVCS = pm.get("vcs")  # type: ignore[assignment]
        # re-bind if the plugin was initialised with a different working tree
        if Path(vcs.repo.working_tree_dir).resolve() != worktree:
            vcs = GitVCS(worktree)

        if results_file := result.get("results_file"):
            analysis_branch = pea_ref("analysis", spec_name)
            vcs.create_branch(analysis_branch, "HEAD", checkout=True)

            # merge run branches using "ours"
            for rd in run_dirs:
                run_branch = pea_ref("run", rd.name)
                vcs.merge_ours(run_branch, f"merge {run_branch}")

            rel_path = os.path.relpath(Path(results_file), worktree)
            commit_sha = vcs.commit([rel_path], f"analysis {spec_name}")
            vcs.switch("HEAD")
            if vcs.has_remote():
                vcs.push(analysis_branch)

            result.update(commit=commit_sha, analysis_branch=analysis_branch)

    return result
