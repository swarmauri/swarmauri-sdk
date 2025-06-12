from __future__ import annotations

import os
import uuid
from typing import Any, Dict, Iterable, List

import httpx

from peagen.models import Task, Status


async def fanout(
    parent: Dict[str, Any] | Task,
    action: str,
    args_list: Iterable[Dict[str, Any]],
    result: Dict[str, Any] | None = None,
    status: Status = Status.waiting,
) -> Dict[str, Any]:
    """Spawn child tasks and patch the parent with their IDs."""
    gateway = os.getenv("DQ_GATEWAY", "http://localhost:8000/rpc")
    pool = parent.get("pool", "default")
    parent_id = parent["id"] if isinstance(parent, dict) else parent.id

    child_ids: List[str] = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for args in args_list:
            child = Task(
                id=str(uuid.uuid4()),
                pool=pool,
                action=action,
                status=Status.waiting,
                payload={"action": action, "args": args},
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
            "params": {"taskId": parent_id, "changes": {"result": {"children": child_ids}}},
        }
        await client.post(gateway, json=patch)

        finish = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "Work.finished",
            "params": {"taskId": parent_id, "status": status.value, "result": result},
        }
        await client.post(gateway, json=finish)

    return {"children": child_ids, **(result or {})}
