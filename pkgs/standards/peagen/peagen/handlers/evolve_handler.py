"""Expand an evolve spec into multiple mutate tasks."""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, List

import yaml

from peagen.models import Task, Status
from .fanout import fan_out


async def evolve_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})

    spec_path = Path(args["evolve_spec"]).expanduser()
    doc = yaml.safe_load(spec_path.read_text())
    jobs: List[Dict[str, Any]] = doc.get("JOBS", [])

    pool = task_or_dict.get("pool", "default")
    children: List[Task] = []
    for job in jobs:
        children.append(
            Task(
                id=str(uuid.uuid4()),
                pool=pool,
                action="mutate",
                status=Status.waiting,
                payload={"action": "mutate", "args": job},
            )
        )

    child_ids = await fan_out(task_or_dict, children, result={"evolve_spec": str(spec_path)}, final_status=Status.waiting)
    return {"children": child_ids, "jobs": len(jobs)}
