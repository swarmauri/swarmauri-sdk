# peagen/handlers/process_handler.py
"""
Unified entry-point for `process` tasks.

• Merges CLI-style overrides with `.peagen.toml`
• Invokes core.process_core helpers
• Returns a JSON-serialisable result mapping
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from autoapi.v2          import AutoAPI
from peagen.orm          import Task

from peagen._utils.config_loader      import resolve_cfg
from peagen.plugins                   import PluginManager
from peagen.plugins.storage_adapters.file_storage_adapter import FileStorageAdapter
from peagen.core.process_core         import (
    load_projects_payload,
    process_single_project,
    process_all_projects,
)

# ─────────────────────────── AutoAPI schema ───────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")                      # incoming model


# ─────────────────────────── main coroutine ───────────────────────────
async def process_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Expected payload structure
    --------------------------
    task.payload == {
        "args": {
            "projects_payload": <str | bytes>,
            "project_name"    : <str | None>,
            "out_dir"         : <str>,
            "start_idx"       : 0,
            "start_file"      : "...",
            "transitive"      : False,
            "config"          : "<cfg.toml>",
            # VCS / agent params …
        },
        "cfg_override": {...}      # optional inline TOML fragments
    }
    """
    payload: Dict[str, Any] = task.payload or {}
    args:    Dict[str, Any] = payload.get("args", {})
    cfg_override            = payload.get("cfg_override", {})

    projects_payload: str | bytes = args["projects_payload"]
    project_name: str | None      = args.get("project_name")

    # ─── merge config (.peagen.toml + overrides) ─────────────────────
    cfg = resolve_cfg(toml_text=cfg_override)

    pm = PluginManager(cfg)
    # storage adapter
    try:
        cfg["storage_adapter"] = pm.get("storage_adapters")
    except Exception:
        file_cfg = cfg.get("storage", {}).get("adapters", {}).get("file", {})
        cfg["storage_adapter"] = FileStorageAdapter(**file_cfg) if file_cfg else None
    # VCS helper
    try:
        cfg["vcs"] = pm.get("vcs")
    except Exception:
        cfg["vcs"] = None

    cfg["agent_env"] = args.get("agent_env", {})

    # ─── dispatch to core logic ───────────────────────────────────────
    if project_name:
        projects = load_projects_payload(projects_payload)
        project  = next(
            (p for p in projects if p.get("NAME") == project_name), None
        )
        if project is None:
            raise ValueError(f"Project '{project_name}' not found in payload")

        processed, _, commit_sha, oids = process_single_project(
            project     = project,
            cfg         = cfg,
            start_idx   = args.get("start_idx", 0),
            start_file  = args.get("start_file"),
            transitive  = args.get("transitive", False),
        )
        return {
            "processed": {project_name: processed},
            "commit"   : commit_sha,
            "oids"     : oids,
        }

    # ---- all projects path ------------------------------------------
    processed_map = process_all_projects(
        projects_payload,
        cfg         = cfg,
        transitive  = args.get("transitive", False),
    )
    return {"processed": processed_map}
