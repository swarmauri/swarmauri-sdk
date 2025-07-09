"""
Async entry-point for “sort” tasks.

Input : TaskRead  – AutoAPI schema mapped to the Task table
Output: dict      – result from sort_core helpers
"""

from __future__ import annotations

from typing import Any, Dict

from autoapi.v2 import AutoAPI
from peagen.orm  import Task

from peagen._utils                 import maybe_clone_repo
from peagen._utils.config_loader   import resolve_cfg
from peagen.core.sort_core         import sort_single_project, sort_all_projects

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")          # validated input model


# ─────────────────────────── main coroutine ───────────────────────────
async def sort_handler(task: TaskRead) -> Dict[str, Any]:
    """
    `task.args` MUST contain
    ------------------------
    {
        "projects_payload":  <str | bytes>,      # required (YAML text or blob URI)
        "project_name"    :  <str | None>,       # optional – single-project mode
        "start_idx"       :  0,
        "start_file"      :  "...",
        "transitive"      :  false,
        "show_dependencies": false,
        "cfg_override"    :  {...},              # optional inline TOML
        "repo"            :  "<git url>",        # optional checkout
        "ref"             :  "HEAD"              # optional
    }
    """
    args: Dict[str, Any]   = task.args or {}
    cfg_override: Dict[str, Any] = args.get("cfg_override", {})

    # ---------- effective configuration -------------------------------
    cfg = resolve_cfg(toml_text=cfg_override)

    params: Dict[str, Any] = {
        "projects_payload" : args["projects_payload"],
        "project_name"     : args.get("project_name"),
        "start_idx"        : args.get("start_idx", 0),
        "start_file"       : args.get("start_file"),
        "transitive"       : args.get("transitive", False),
        "show_dependencies": args.get("show_dependencies", False),
        "cfg"              : cfg,
    }

    repo: str | None = args.get("repo")
    ref:  str        = args.get("ref", "HEAD")

    # ---------- delegate to core logic --------------------------------
    with maybe_clone_repo(repo, ref):            # no-op if repo is None
        if params["project_name"]:
            return sort_single_project(params)
        return sort_all_projects(params)
