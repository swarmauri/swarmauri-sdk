# peagen/handlers/sort_handler.py

from typing import Any, Dict
from peagen.core.sort_core import (
    sort_single_project,
    sort_all_projects,
    _merge_cli_into_toml,
)
from peagen.models import Task


async def sort_handler(task: Dict[str, Any] | Task) -> Dict[str, Any]:
    """
    Handler invoked when payload.action == "sort".
    Expects task["payload"]["args"] to include exactly:
      - projects_payload
      - project_name (optional)
      - start_idx
      - start_file (optional)
      - verbose
      - transitive
      - show_dependencies
    """
    payload = task.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})

    params = _merge_cli_into_toml(
        projects_payload=args["projects_payload"],
        project_name=args.get("project_name"),
        start_idx=args.get("start_idx"),
        start_file=args.get("start_file"),
        verbose=args.get("verbose", 0),
        transitive=args.get("transitive", False),
        show_dependencies=args.get("show_dependencies", False),
    )

    if params["project_name"]:
        return sort_single_project(params)
    else:
        return sort_all_projects(params)
