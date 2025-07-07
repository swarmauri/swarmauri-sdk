# peagen/handlers/sort_handler.py
"""
Async entry-point for “sort” tasks.

Input : TaskRead  – AutoAPI schema mapped to the Task ORM table
Output: dict      – result returned by sort_core helpers
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from autoapi import AutoAPI
from autoapi.v2.tables.task import Task                       # ORM class

from peagen._utils                 import maybe_clone_repo
from peagen._utils.config_loader   import resolve_cfg
from peagen.core.sort_core         import sort_single_project, sort_all_projects

# ─────────────────────────── AutoAPI schema ───────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")                   # incoming model


# ─────────────────────────── main coroutine ───────────────────────────
async def sort_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Expected task.payload
    ---------------------
    {
        "args": {
            "projects_payload": <str | bytes>,
            "project_name"    : <str | None>,
            "start_idx"       : 0,
            "start_file"      : "...",
            "transitive"      : False,
            "show_dependencies": False,
            "cfg_override"    : {...}          # optional TOML fragments
            "repo"            : "<git-url>",
            "ref"             : "HEAD"
        }
    }
    """
    payload: Dict[str, Any] = task.payload or {}
    args:    Dict[str, Any] = payload.get("args", {})
    cfg_override            = payload.get("cfg_override", {})

    # ----- effective configuration ------------------------------------
    cfg = resolve_cfg(toml_text=cfg_override)

    params: Dict[str, Any] = {
        "projects_payload": args["projects_payload"],
        "project_name"    : args.get("project_name"),
        "start_idx"       : args.get("start_idx", 0),
        "start_file"      : args.get("start_file"),
        "transitive"      : args.get("transitive", False),
        "show_dependencies": args.get("show_dependencies", False),
        "cfg"             : cfg,
    }

    repo = args.get("repo")
    ref  = args.get("ref", "HEAD")

    # ----- delegate to core business logic ----------------------------
    with maybe_clone_repo(repo, ref):                      # no-op when repo is None
        if params["project_name"]:
            return sort_single_project(params)
        return sort_all_projects(params)
