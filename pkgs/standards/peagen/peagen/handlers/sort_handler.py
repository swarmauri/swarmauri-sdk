# peagen/handlers/sort_handler.py
"""
Gateway / worker handler for the **sort** action.

Expected task payload
---------------------
{
  "action": "sort",
  "args": {                       # ← per-command flags
      "projects_payload": "...",  # YAML text **or** path
      "project_name": null,
      "start_idx": 0,
      "start_file": null,
      "transitive": false,
      "show_dependencies": false
  },
  "batch_cfg": { ... }            # ← overrides shared by the whole submit batch
}
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import os

from peagen.core.sort_core import sort_single_project, sort_all_projects
from peagen._utils.config_loader import resolve_cfg


async def sort_handler(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async handler registered under JSON-RPC method ``Task.sort`` (or similar).

    • Delegates to sort_core.
    • Returns whatever the core returns (sorted list or error dict).
    """
    payload = task.get("payload", {})
    args = payload.get("args", {})
    cfg_override = payload.get("cfg_override", {})
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")
    tmp_dir = None
    prev_cwd = None
    if repo:
        from peagen.core.fetch_core import fetch_single
        import tempfile

        tmp_dir = Path(tempfile.mkdtemp(prefix="peagen_repo_"))
        fetch_single(repo=repo, ref=ref, dest_root=tmp_dir)
        prev_cwd = Path.cwd()
        os.chdir(tmp_dir)

    # ------------------------------------------------------------------ #
    # 1) Build the effective configuration for *this* task
    # ------------------------------------------------------------------ #
    cfg = resolve_cfg(toml_text=cfg_override)

    # ------------------------------------------------------------------ #
    # 2) Re-package params for sort_core
    # ------------------------------------------------------------------ #
    params: Dict[str, Any] = {
        "projects_payload": args["projects_payload"],
        "project_name": args.get("project_name"),
        "start_idx": args.get("start_idx", 0),
        "start_file": args.get("start_file"),
        "transitive": args.get("transitive", False),
        "show_dependencies": args.get("show_dependencies", False),
        "cfg": cfg,  # ← merged config handed down to the core
    }

    # ------------------------------------------------------------------ #
    # 3) Delegate to core (single or all projects)
    # ------------------------------------------------------------------ #
    try:
        if params["project_name"]:
            result = sort_single_project(params)
        else:
            result = sort_all_projects(params)
    finally:
        if repo and tmp_dir and prev_cwd:
            import shutil

            os.chdir(prev_cwd)
            shutil.rmtree(tmp_dir, ignore_errors=True)
    return result
