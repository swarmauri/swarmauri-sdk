from __future__ import annotations

import os
import uuid
from typing import Iterable, List, Dict, Any

import httpx

from peagen.schemas import TaskRead
from peagen.orm.status import Status
from peagen.protocols.methods import (
    TASK_SUBMIT,
    TASK_PATCH,
    WORK_FINISHED,
)
from . import ensure_task


async def fan_out(
    parent: TaskRead | Dict[str, Any],
    children: Iterable[TaskRead],
    *,
    result: Dict[str, Any] | None = None,
    final_status: Status = Status.waiting,
) -> Dict[str, Any]:
    """Submit *children* and update *parent* with their IDs."""
    gateway = os.getenv("DQ_GATEWAY", "http://localhost:8000/rpc")
    canonical_parent = ensure_task(parent)
    parent_id = canonical_parent.id

    child_ids: List[str] = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for child in children:
            req = {
                "jsonrpc": "2.0",
                "method": TASK_SUBMIT,
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
            "method": TASK_PATCH,
            "params": {
                "taskId": parent_id,
                "changes": {"result": {"children": child_ids}},
            },
        }
        await client.post(gateway, json=patch)

        finish = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": WORK_FINISHED,
            "params": {
                "taskId": parent_id,
                "status": final_status.value,
                "result": result,
            },
        }
        await client.post(gateway, json=finish)

    return {"children": child_ids, "_final_status": final_status.value}
