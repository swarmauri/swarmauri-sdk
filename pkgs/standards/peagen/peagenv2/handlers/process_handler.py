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

from peagen.core.process_core import (
    merge_cli_into_cfg,
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
    if not isinstance(task, dict):
        task = task.model_dump()  # type: ignore[attr-defined]

    payload: Dict[str, Any] = task.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})

    # Mandatory flag
    projects_payload: str = args["projects_payload"]

    # ------------------------------------------------------------------ #
    # 1) Merge .peagen.toml with CLI-style overrides
    # ------------------------------------------------------------------ #
    cfg = merge_cli_into_cfg(
        projects_payload=projects_payload,
        start_idx=args.get("start_idx", 0),
        start_file=args.get("start_file"),
        transitive=args.get("transitive", False),
        verbose=args.get("verbose", 0),
        output_base=args.get("output_base"),
    )

    # Pass through any LLM / agent parameters verbatim
    cfg["agent_env"] = args.get("agent_env", {})

    # ------------------------------------------------------------------ #
    # 2) Dispatch to core business logic
    # ------------------------------------------------------------------ #
    project_name: str | None = args.get("project_name")
    if project_name:
        projects = load_projects_payload(projects_payload)
        project = next(
            (p for p in projects if p.get("NAME") == project_name), None
        )
        if project is None:  # defensive
            raise ValueError(f"Project '{project_name}' not found in payload!")
        processed, _ = process_single_project(
            project=project,
            cfg=cfg,
            start_idx=args.get("start_idx", 0),
            start_file=args.get("start_file"),
            transitive=args.get("transitive", False),
            verbose=args.get("verbose", 0),
            output_base=args.get("output_base"),
        )
        result_map: Dict[str, List[Dict[str, Any]]] = {project_name: processed}
    else:
        result_map = process_all_projects(
            projects_payload_path=projects_payload,
            cfg=cfg,
            transitive=args.get("transitive", False),
            verbose=args.get("verbose", 0),
            output_base=args.get("output_base"),
        )

    # ------------------------------------------------------------------ #
    # 3) Shape unified response
    # ------------------------------------------------------------------ #
    return {
        "processed": result_map,
        "manifest": cfg.get("manifest_path"),  # may be None
    }
