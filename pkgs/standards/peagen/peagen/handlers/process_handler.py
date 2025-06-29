# peagen/handlers/process_handler.py
"""
Unified entry-point for ``process`` tasks.

The handler merges CLI-style overrides with ``.peagen.toml``,
invokes the appropriate functions in **process_core**, and
returns a JSON-serialisable result mapping.
"""

from __future__ import annotations

from swarmauri_standard.loggers.Logger import Logger
from typing import Any, Dict, List
from pathlib import Path
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.storage_adapters.file_storage_adapter import FileStorageAdapter

from peagen.core.process_core import (
    load_projects_payload,
    process_single_project,
    process_all_projects,
)
from peagen.transport.jsonrpc_schemas.task import SubmitParams, SubmitResult

logger = Logger(name=__name__)


async def process_handler(task: SubmitParams) -> SubmitResult:
    """Main coroutine invoked by workers and synchronous CLI runs."""
    # ------------------------------------------------------------------ #
    # 0) Normalise input
    # ------------------------------------------------------------------ #
    payload: Dict[str, Any] = task.payload
    args: Dict[str, Any] = payload.get("args", {})
    cfg_override = payload.get("cfg_override", {})
    # Mandatory flag
    projects_payload = args["projects_payload"]
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")
    tmp_dir = None
    if repo:
        from peagen.core.fetch_core import fetch_single
        import tempfile
        import os

        tmp_dir = Path(tempfile.mkdtemp(prefix="peagen_repo_"))
        fetch_single(repo=repo, ref=ref, dest_root=tmp_dir)
        prev_cwd = Path.cwd()
        os.chdir(tmp_dir)

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
        file_cfg = cfg.get("storage", {}).get("adapters", {}).get("file", {})
        try:
            cfg["storage_adapter"] = FileStorageAdapter(**file_cfg)
        except Exception:
            cfg["storage_adapter"] = None

    try:
        cfg["vcs"] = pm.get("vcs")
    except Exception:  # pragma: no cover - optional
        cfg["vcs"] = None

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
        processed, _, commit_sha, oids = process_single_project(
            project=project,
            cfg=cfg,
            start_idx=args.get("start_idx", 0),
            start_file=args.get("start_file"),
            transitive=args.get("transitive", False),
        )
        result_map: Dict[str, List[Dict[str, Any]]] = {project_name: processed}
        result = {"processed": result_map, "commit": commit_sha, "oids": oids}
    else:
        result_map = process_all_projects(
            projects_payload,
            cfg=cfg,
            transitive=args.get("transitive", False),
        )
        result = {"processed": result_map}
    if repo and tmp_dir:
        import shutil
        import os

        os.chdir(prev_cwd)
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return result
