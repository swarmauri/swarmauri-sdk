"""
peagen.handlers.mutate_handler
──────────────────────────────
Async entry-point for the *mutate* workflow.

Changes vs. legacy
------------------
* Does **not** create a throw-away clone; the heavy-lifting is done by
  :func:`peagen.core.mutate_core.mutate_workspace`, which creates an
  isolated work-tree under repo-level locking.
* No storage-adapter logic.
* `workspace_uri` parameter is gone.
"""

from __future__ import annotations

import os
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict

from tigrbl import get_schema
from peagen.orm import Task
from peagen.core.mutate_core import mutate_workspace
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import GitVCS, pea_ref

# ─────────────────────────── schema handle ──────────────────────────
TaskRead = get_schema(Task, "read")


# ─────────────────────────── coroutine ──────────────────────────────
async def mutate_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Expected *task.args*::

        {
            "repo":         "<git-url>",          # required
            "ref":          "main",               # optional (default HEAD)
            "target_file":  "src/foo.py",         # required – relative to repo root
            "import_path":  "pkg.module",         # required
            "entry_fn":     "benchmark",          # required
            "gens":         3,                    # optional
            "mutations":    [...],                # optional
            "profile_mod":  "prof",               # optional
            "config":       "path/to/.toml",      # optional – inside repo
            "evaluator":    "performance_evaluator"  # optional
        }
    """
    args: Dict[str, Any] = task.args or {}
    repo: str = args["repo"]
    ref: str = args.get("ref", "HEAD")

    cfg_path = Path(args["config"]).expanduser() if args.get("config") else None

    # ── 1. run mutation --------------------------------------------------
    result = mutate_workspace(
        repo=repo,
        ref=ref,
        target_file=args["target_file"],
        import_path=args["import_path"],
        entry_fn=args["entry_fn"],
        gens=int(args.get("gens", 1)),
        profile_mod=args.get("profile_mod"),
        cfg_path=cfg_path,
        mutations=args.get("mutations"),
        evaluator_ref=args.get("evaluator", "performance_evaluator"),
    )

    # ── 2. optional VCS commit ------------------------------------------
    cfg = resolve_cfg(toml_path=str(cfg_path) if cfg_path else None)
    pm = PluginManager(cfg)
    with suppress(Exception):
        vcs: GitVCS = pm.get("vcs")  # type: ignore[assignment]
        worktree = Path(result["worktree"]).resolve()
        if Path(vcs.repo.working_tree_dir).resolve() != worktree:
            # re-bind the VCS instance to the correct work-tree
            vcs = GitVCS(worktree)

        winner_path = Path(result["winner"]).resolve()
        rel_winner = os.path.relpath(winner_path, worktree)
        commit_sha = vcs.commit([rel_winner], f"mutate {winner_path.name}")
        result["winner_oid"] = vcs.blob_oid(rel_winner)

        branch = pea_ref("run", winner_path.stem)
        vcs.create_branch(branch, checkout=False)
        if vcs.has_remote():
            vcs.push(branch)

        result.update(commit=commit_sha, branch=branch)

    return result
