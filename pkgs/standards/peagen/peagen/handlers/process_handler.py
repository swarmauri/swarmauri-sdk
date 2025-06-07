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

import logging
from typing import Any, Dict, List
from peagen._utils.config_loader import resolve_cfg

from peagen.core.process_core import (
    load_projects_payload,
    process_single_project,
    process_all_projects,
)
from peagen.models import Task, Status  # noqa: F401 – used by type hints

logger = logging.getLogger(__name__)


async def process_handler(task: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Main coroutine invoked by workers and synchronous CLI runs."""
    # ------------------------------------------------------------------ #
    # 0) Normalise input – accept Task *or* plain dict
    # ------------------------------------------------------------------ #
    payload: Dict[str, Any] = task.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})
    cfg_override = payload.get("cfg_override", {})
    # Mandatory flag
    projects_payload: str = args["projects_payload"]

    # ------------------------------------------------------------------ #
    # 1) Merge .peagen.toml with CLI-style overrides
    # ------------------------------------------------------------------ #
    cfg = resolve_cfg(toml_text=cfg_override)

    # Merge CLI-provided agent_env with defaults from config
    agent_env = args.get("agent_env", {})
    llm_cfg = cfg.get("llm", {})
    # Fill missing fields from llm defaults
    agent_env.setdefault("provider", llm_cfg.get("default_provider"))
    agent_env.setdefault("model_name", llm_cfg.get("default_model_name"))
    agent_env.setdefault("temperature", llm_cfg.get("default_temperature"))
    agent_env.setdefault("max_tokens", llm_cfg.get("default_max_tokens"))

    provider = agent_env.get("provider")
    if provider:
        # Look for API key under [llm.<provider>] or [llm.api_keys]
        api_key = agent_env.get("api_key")
        if not api_key:
            api_key = llm_cfg.get(provider, {}).get("API_KEY")
            if not api_key:
                api_key = llm_cfg.get("api_keys", {}).get(provider)
        if api_key:
            agent_env["api_key"] = api_key

    cfg["agent_env"] = agent_env

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
        )
        result_map: Dict[str, List[Dict[str, Any]]] = {project_name: processed}
    else:
        result_map = process_all_projects(
            projects_payload_path=projects_payload,
            cfg=cfg,
            transitive=args.get("transitive", False),
        )

    # ------------------------------------------------------------------ #
    # 3) Shape unified response
    # ------------------------------------------------------------------ #
    return {
        "processed": result_map,
        "manifest": cfg.get("manifest_path"),  # may be None
    }