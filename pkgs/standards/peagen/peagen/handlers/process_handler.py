# peagen/handlers/process_handler.py
"""
Unified entry-point for “process” tasks.

A worker (or a local CLI run) will pass in either:
  • a plain ``dict`` decoded from JSON-RPC, or
  • a ``peagen.models.Task`` instance.

The handler merges CLI-style overrides with ``.peagen.toml``,
invokes the appropriate functions in **process_core**, and
returns a JSON-serialisable result mapping.
"""

from __future__ import annotations

from swarmauri_standard.loggers.Logger import Logger
from typing import Any, Dict, List
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.storage_adapters.file_storage_adapter import FileStorageAdapter

from peagen.core.process_core import (
    load_projects_payload,
    process_single_project,
    process_all_projects,
)
from peagen.models import Task, Status  # noqa: F401 – used by type hints

logger = Logger(name=__name__)


async def process_handler(task: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Main coroutine invoked by workers and synchronous CLI runs."""
    # ------------------------------------------------------------------ #
    # 0) Normalise input – accept Task *or* plain dict
    # ------------------------------------------------------------------ #
    payload: Dict[str, Any] = task.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})
    cfg_override = payload.get("cfg_override", {})
    # Mandatory flag
    projects_payload = args["projects_payload"]

    # ------------------------------------------------------------------ #
    # 1) Merge .peagen.toml with CLI-style overrides
    # ------------------------------------------------------------------ #
    cfg = resolve_cfg(toml_text=cfg_override)

    # Instantiate plugins so core functions receive ready-to-use objects
    pm = PluginManager(cfg)
    try:
        cfg["storage_adapter"] = pm.get("storage_adapters")
    except Exception:  # pragma: no cover - optional
        # Fall back to FileStorageAdapter if configured
        file_cfg = (
            cfg.get("storage", {})
            .get("adapters", {})
            .get("file", {})
        )
        try:
            cfg["storage_adapter"] = FileStorageAdapter(**file_cfg)
        except Exception:
            cfg["storage_adapter"] = None

    # Pass through any LLM / agent parameters verbatim
    cfg["agent_env"] = args.get("agent_env", {})

    # ------------------------------------------------------------------ #
    # 2) Dispatch to core business logic
    # ------------------------------------------------------------------ #
    project_name: str | None = args.get("project_name")
    if project_name:
        projects = load_projects_payload(projects_payload)
        project = next((p for p in projects if p.get("NAME") == project_name), None)
        if project is None:  # defensive
            raise ValueError(f"Project '{project_name}' not found in payload!")
        processed, _ = process_single_project(
            project=project,
            cfg=cfg,
            start_idx=args.get("start_idx", 0),
            start_file=args.get("start_file"),
            transitive=args.get("transitive", False),
            parent_task_id=task.get("id"),
        )
        result_map: Dict[str, List[Dict[str, Any]]] = {project_name: processed}
    else:
        result_map = process_all_projects(
            projects_payload,
            cfg=cfg,
            transitive=args.get("transitive", False),
            parent_task_id=task.get("id"),
        )

    # ------------------------------------------------------------------ #
    # 3) Shape unified response
    # ------------------------------------------------------------------ #
    return {
        "processed": result_map,
        "manifest": cfg.get("manifest_path"),  # may be None
    }
