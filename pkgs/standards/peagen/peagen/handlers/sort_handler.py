"""
peagen.handlers.sort_handler
────────────────────────────
Async entry-point for *sort* tasks.

Changes vs. legacy
------------------
* No `maybe_clone_repo` – the handler operates inside the caller-supplied
  **worktree** (an existing Git work-tree for the task).
* No storage-adapter logic or repo cloning code.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from tigrbl.v3 import get_schema
from peagen.orm import Task

from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import GitVCS
from peagen.core.sort_core import sort_single_project, sort_all_projects

# ───────────────────── schema handle ────────────────────────────────
TaskRead = get_schema(Task, "read")


# ───────────────────── main coroutine ───────────────────────────────
async def sort_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Expected ``task.args``::

        {
            "projects_payload": <str|bytes>,   # YAML text or blob URI
            "worktree":        "<abs path>",   # required – task work-tree
            "project_name":    "<str>",        # optional single-project mode
            "start_idx":       0,              # optional
            "start_file":      "...",          # optional
            "transitive":      false,          # optional
            "show_dependencies": false,        # optional
            "config":          "<cfg.toml>",   # optional – inside worktree or abs
        }
    """
    args: Dict[str, Any] = task.args or {}

    worktree = Path(args["worktree"]).expanduser().resolve()
    if not worktree.exists():
        raise FileNotFoundError(f"worktree not found: {worktree}")

    projects_payload = args["projects_payload"]
    project_name = args.get("project_name")

    # ─── configuration & plugins ─────────────────────────────────────
    cfg_path = (
        Path(args["config"]).expanduser()
        if args.get("config")
        else worktree / ".peagen.toml"
    )
    cfg = resolve_cfg(toml_path=str(cfg_path) if cfg_path.exists() else None)
    cfg["worktree"] = worktree

    pm = PluginManager(cfg)
    try:
        vcs: GitVCS = pm.get("vcs")  # type: ignore[assignment]
        # ensure VCS is bound to the correct work-tree
        if Path(vcs.repo.working_tree_dir).resolve() != worktree:
            vcs = GitVCS(worktree)
        cfg["vcs"] = vcs
    except Exception:
        cfg["vcs"] = None

    params: Dict[str, Any] = {
        "projects_payload": projects_payload,
        "project_name": project_name,
        "start_idx": int(args.get("start_idx", 0)),
        "start_file": args.get("start_file"),
        "transitive": args.get("transitive", False),
        "show_dependencies": args.get("show_dependencies", False),
        "cfg": cfg,
    }

    # ─── delegate to core.sort_core ──────────────────────────────────
    if project_name:
        return sort_single_project(params)

    return sort_all_projects(params)
