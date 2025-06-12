from __future__ import annotations

import os
import uuid
from typing import Iterable, List, Dict, Any

import httpx

from peagen.models import Task, Status


async def fan_out(
    parent: Task | Dict[str, Any],
    children: Iterable[Task],
    *,
    result: Dict[str, Any] | None = None,
    final_status: Status = Status.waiting,
) -> List[str]:
    """Submit *children* and update *parent* with their IDs."""
    gateway = os.getenv("DQ_GATEWAY", "http://localhost:8000/rpc")
    parent_id = parent.get("id") if isinstance(parent, dict) else parent.id

    child_ids: List[str] = []
    batch: List[Dict[str, Any]] = []
    for child in children:
        batch.append(
            {
                "jsonrpc": "2.0",
                "method": "Task.submit",
                "params": {
                    "taskId": child.id,
                    "pool": child.pool,
                    "payload": child.payload,
                },
            }
        )
        child_ids.append(child.id)

    batch.append(
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "Task.patch",
            "params": {"taskId": parent_id, "changes": {"result": {"children": child_ids}}},
        }
    )

    batch.append(
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "Work.finished",
            "params": {"taskId": parent_id, "status": final_status.value, "result": result},
        }
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(gateway, json=batch)

    return child_ids
