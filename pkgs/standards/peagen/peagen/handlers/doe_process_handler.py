# peagen/handlers/doe_process_handler.py
"""Handler for DOE workflow that spawns process tasks."""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any, Dict, List

import httpx
import yaml

from peagen.core.doe_core import generate_payload
from peagen.models import Task, Status


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

    gateway = os.getenv("DQ_GATEWAY", "http://localhost:8000/rpc")
    pool = task_or_dict.get("pool", "default")

    child_ids: List[str] = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for proj in projects:
            child = Task(
                    id=str(uuid.uuid4()),
                    pool=pool,
                    action="process",
                    status=Status.waiting,
                    payload={
                        "action": "process",
                        "args": {
                            "projects_payload": result["output"],
                            "project_name": proj.get("NAME"),
                        },
                    },
            )
            req = {
                "jsonrpc": "2.0",
                "method": "Task.submit",
                "params": {
                    "taskId": child.id,
                    "pool": child.pool,
                    "payload": child.payload,
                },
            }
            await client.post(gateway, json=req)
            child_ids.append(child.id)

        patch = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "Task.patch",
            "params": {"taskId": task_or_dict["id"], "changes": {"result": {"children": child_ids}}},
        }
        await client.post(gateway, json=patch)

        finish = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "Work.finished",
            "params": {"taskId": task_or_dict["id"], "status": "waiting", "result": result},
        }
        await client.post(gateway, json=finish)

    return {"children": child_ids, **result}
