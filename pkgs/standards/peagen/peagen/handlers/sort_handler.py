# peagen/handlers/sort_handler.py

from __future__ import annotations
from typing import Any, Dict

from peagen.transport.jsonrpc_schemas.task import SubmitParams, SubmitResult

from . import ensure_task

from peagen._utils import maybe_clone_repo

from peagen.core.sort_core import sort_single_project, sort_all_projects
from peagen._utils.config_loader import resolve_cfg


async def sort_handler(task: Dict[str, Any] | SubmitParams) -> SubmitResult:
    """
    Async handler registered under JSON-RPC method ``Task.sort`` (or similar).

    • Delegates to sort_core.
    • Returns whatever the core returns (sorted list or error dict).
    """
    task = ensure_task(task)
    payload = task.payload
    args = payload.get("args", {})
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")
    cfg_override = payload.get("cfg_override", {})

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
    with maybe_clone_repo(repo, ref):
        if params["project_name"]:
            return sort_single_project(params)
        return sort_all_projects(params)
