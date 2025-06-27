from __future__ import annotations

import os
import uuid
from typing import Iterable, List, Dict, Any

import httpx

from peagen.models.task import Task
from peagen.models.task.status import Status


async def fan_out(
    parent: Task | Dict[str, Any],
    children: Iterable[Task],
    *,
    result: Dict[str, Any] | None = None,
    final_status: Status = Status.waiting,
) -> Dict[str, Any]:
    """Submit *children* and update *parent* with their IDs."""
    gateway = os.getenv("DQ_GATEWAY", "http://localhost:8000/rpc")
    parent_id = parent.get("id") if isinstance(parent, dict) else parent.id

    child_ids: List[str] = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for child in children:
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
            "params": {
                "taskId": parent_id,
                "changes": {"result": {"children": child_ids}},
            },
        }
        await client.post(gateway, json=patch)

        finish = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "Work.finished",
            "params": {
                "taskId": parent_id,
                "status": final_status.value,
                "result": result,
            },
        }
        await client.post(gateway, json=finish)

    return {"children": child_ids, "_final_status": final_status.value}
