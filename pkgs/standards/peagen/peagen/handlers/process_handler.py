"""
Unified entry-point for *process* tasks.

• Merges CLI-style overrides with `.peagen.toml`
• Invokes helpers from `peagen.core.process_core`
• Returns a JSON-serialisable result mapping
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from autoapi.v2 import AutoAPI
from peagen.orm  import Task

from peagen._utils.config_loader                     import resolve_cfg
from peagen.plugins                                  import PluginManager
from peagen.plugins.storage_adapters.file_storage_adapter import FileStorageAdapter
from peagen.core.process_core                        import (
    load_projects_payload,
    process_single_project,
    process_all_projects,
)

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")          # validated Pydantic model


# ─────────────────────────── main coroutine ───────────────────────────
async def process_handler(task: TaskRead) -> Dict[str, Any]:
    """
    `task.args` MUST contain
    ------------------------
    {
        "projects_payload":  <str | bytes>,          # YAML text or blob URI
        "project_name"    :  <str | None>,           # optional single-project mode
        "out_dir"         :  <str>,                  # default ./out
        "start_idx"       :  0,
        "start_file"      :  "...",
        "transitive"      :  false,
        "config"          :  "<cfg.toml>",           # optional
        "agent_env"       :  {...},                  # optional – forwarded to core
        "cfg_override"    :  {...},                  # optional inline TOML
        # optional VCS / repo settings may be present but are ignored here
    }
    """
    args: Dict[str, Any] = task.args or {}
    cfg_override: Dict[str, Any] = args.get("cfg_override", {})

    projects_payload: str | bytes = args["projects_payload"]
    project_name: str | None      = args.get("project_name")

    # ─── merge config file with inline overrides ──────────────────────
    cfg = resolve_cfg(toml_text=cfg_override,
                      toml_path=args.get("config", ".peagen.toml"))

    pm = PluginManager(cfg)

    # Storage adapter (fallback to local file adapter)
    try:
        cfg["storage_adapter"] = pm.get("storage_adapters")
    except Exception:                                   # pragma: no cover
        file_cfg = cfg.get("storage", {}).get("adapters", {}).get("file", {})
        cfg["storage_adapter"] = FileStorageAdapter(**file_cfg) if file_cfg else None

    # VCS helper (optional)
    try:
        cfg["vcs"] = pm.get("vcs")
    except Exception:                                   # pragma: no cover
        cfg["vcs"] = None

    cfg["agent_env"] = args.get("agent_env", {})

    # ─── single-project path ──────────────────────────────────────────
    if project_name:
        projects = load_projects_payload(projects_payload)
        project  = next((p for p in projects if p.get("NAME") == project_name), None)
        if project is None:
            raise ValueError(f"Project '{project_name}' not found in payload")

        processed, _, commit_sha, oids = process_single_project(
            project      = project,
            cfg          = cfg,
            start_idx    = args.get("start_idx", 0),
            start_file   = args.get("start_file"),
            transitive   = args.get("transitive", False),
        )
        return {
            "processed": {project_name: processed},
            "commit":    commit_sha,
            "oids":      oids,
        }

    # ─── all-projects path ────────────────────────────────────────────
    processed_map = process_all_projects(
        projects_payload,
        cfg        = cfg,
        transitive = args.get("transitive", False),
    )
    return {"processed": processed_map}
