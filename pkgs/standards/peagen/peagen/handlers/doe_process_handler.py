# peagen/handlers/doe_process_handler.py
"""Handler for DOE workflow that spawns process tasks."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from peagen.core.doe_core import generate_payload
from peagen.models import Task
from peagen.handlers.fanout import fanout


async def doe_process_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Expand the DOE spec and spawn a process task for each project."""
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})

    result = generate_payload(
        spec_path=Path(args["spec"]).expanduser(),
        template_path=Path(args["template"]).expanduser(),
        output_path=Path(args["output"]).expanduser(),
        cfg_path=Path(args["config"]).expanduser() if args.get("config") else None,
        notify_uri=args.get("notify"),
        dry_run=args.get("dry_run", False),
        force=args.get("force", False),
        skip_validate=args.get("skip_validate", False),
    )

    doc = yaml.safe_load(Path(result["output"]).read_text())
    projects: List[Dict[str, Any]] = doc.get("PROJECTS", [])

    child_args = [
        {
            "projects_payload": result["output"],
            "project_name": proj.get("NAME"),
        }
        for proj in projects
    ]

    return await fanout(task_or_dict, "process", child_args, result)
