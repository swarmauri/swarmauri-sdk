# peagen/handlers/doe_process_handler.py
"""Handler for DOE workflow that spawns process tasks."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import uuid

import yaml  # type: ignore[import-untyped]

from peagen.core.doe_core import generate_payload
from peagen.core import lock_plan, TaskChainer, chain_hash
from peagen.models import Task, Status
from .fanout import fan_out


async def doe_process_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Expand the DOE spec and spawn a process task for each project."""
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})

    spec_path = Path(args["spec"]).expanduser()
    template_path = Path(args["template"]).expanduser()

    result = generate_payload(
        spec_path=spec_path,
        template_path=template_path,
        output_path=Path(args["output"]).expanduser(),
        cfg_path=Path(args["config"]).expanduser() if args.get("config") else None,
        notify_uri=args.get("notify"),
        dry_run=args.get("dry_run", False),
        force=args.get("force", False),
        skip_validate=args.get("skip_validate", False),
    )

    lock_hash = chain_hash(lock_plan(template_path).encode(), lock_plan(spec_path))
    chainer = TaskChainer(lock_hash)
    if isinstance(task_or_dict, Task):
        task_or_dict.lock_hash = lock_hash
        task_or_dict.chain_hash = lock_hash

    artifact_data = Path(result["output"]).read_bytes()
    chainer.add_artifact(artifact_data)
    doc = yaml.safe_load(artifact_data)
    projects: List[Dict[str, Any]] = doc.get("PROJECTS", [])

    pool = task_or_dict.get("pool", "default")
    children: List[Task] = []
    for proj in projects:
        child = Task(  # type: ignore[call-arg]
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
            lock_hash=lock_hash,
        )
        child.chain_hash = chainer.add_task(child.payload)
        children.append(child)

    child_ids = await fan_out(task_or_dict, children, result=result, final_status=Status.waiting)
    return {"children": child_ids, "lock_hash": lock_hash, "chain_hash": chainer.current_hash, **result}
