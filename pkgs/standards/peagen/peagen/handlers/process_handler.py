"""
peagen.handlers.process_handler
───────────────────────────────
Unified entry-point for *process* tasks.

Key updates
-----------
* **No storage adapters** – artefacts are committed directly to the task’s
  Git work-tree; uploads have been removed.
* Caller **must** supply a **worktree** path (created earlier in the pipeline)
  so that the core logic can commit within the correct repository.
* CLI-style overrides (`cfg_override`, `out_dir`, etc.) have been dropped for
  simplicity and consistency with the new work-tree-first contract.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from tigrbl import get_schema
from peagen.orm import Task

from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import GitVCS
from peagen.core.process_core import (
    load_projects_payload,
    process_single_project,
    process_all_projects,
)

# ───────────────────────── schema handle ────────────────────────────
TaskRead = get_schema(Task, "read")


# ───────────────────────── main coroutine ───────────────────────────
async def process_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Expected ``task.args``::

        {
            "projects_payload": <str|bytes>,   # YAML text or blob URI
            "worktree":        "<path>",       # ABS path to task work-tree (required)
            "project_name":    "<str>",        # optional – single-project mode
            "start_idx":       0,              # optional
            "start_file":      "...",          # optional
            "transitive":      false,          # optional
            "config":          "<cfg.toml>",   # optional – repo-relative or abs
            "agent_env":       {...}           # optional – forwarded to core
        }
    """
    args: Dict[str, Any] = task.args or {}

    worktree = Path(args["worktree"]).expanduser().resolve()
    if not worktree.exists():
        raise FileNotFoundError(f"worktree path not found: {worktree}")

    projects_payload: str | bytes = args["projects_payload"]
    project_name: str | None = args.get("project_name")

    # ─── Configuration & plugin manager ──────────────────────────────
    cfg_path = (
        Path(args["config"]).expanduser()
        if args.get("config")
        else worktree / ".peagen.toml"
    )
    cfg = resolve_cfg(toml_path=str(cfg_path) if cfg_path.exists() else None)
    cfg["worktree"] = worktree
    cfg["agent_env"] = args.get("agent_env", {})

    pm = PluginManager(cfg)

    # bind VCS to the supplied work-tree (if plugin available)
    try:
        vcs: GitVCS = pm.get("vcs")  # type: ignore[assignment]
        if Path(vcs.repo.working_tree_dir).resolve() != worktree:
            vcs = GitVCS(worktree)  # re-bind
        cfg["vcs"] = vcs
    except Exception:
        cfg["vcs"] = None

    # ─── Single-project path ─────────────────────────────────────────
    if project_name:
        projects = load_projects_payload(projects_payload)
        project = next((p for p in projects if p.get("NAME") == project_name), None)
        if project is None:
            raise ValueError(f"Project '{project_name}' not found in payload")

        processed, _, commit_sha, oids = process_single_project(
            project=project,
            cfg=cfg,
            start_idx=int(args.get("start_idx", 0)),
            start_file=args.get("start_file"),
            transitive=args.get("transitive", False),
        )
        return {
            "processed": {project_name: processed},
            "commit": commit_sha,
            "oids": oids,
        }

    # ─── All-projects path ───────────────────────────────────────────
    processed_map = process_all_projects(
        projects_payload,
        cfg=cfg,
        transitive=args.get("transitive", False),
    )
    return {"processed": processed_map}
