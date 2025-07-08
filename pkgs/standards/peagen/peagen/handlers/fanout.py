"""
peagen.handlers.fanout
──────────────────────
Utility that fan-outs a *parent* task into multiple *child* tasks via the
JSON-RPC gateway.

• Accepts plain dictionaries that already conform to AutoAPI’s Tasks.create
  input schema.
• Uses httpx.AsyncClient – keeps the coroutine non-blocking.
"""

from __future__ import annotations

import uuid
from typing import Iterable, Dict, Any, List

import httpx

from peagen.orm import Status
from peagen.defaults import GATEWAY_URL


async def fan_out(  # noqa: C901 for clarity
    parent: Dict[str, Any] | Any,  # TaskRead or a dict with .id attribute
    children: Iterable[Dict[str, Any]],
    *,
    result: Dict[str, Any] | None = None,
    final_status: Status = Status.WAITING,
) -> Dict[str, Any]:
    """
    Submit *children*, patch *parent* with their ids, and mark the parent
    `Work.finished`.

    Returns
    -------
    dict     {"children": [...], "_final_status": <str>}
    """
    parent_id = str(parent["id"] if isinstance(parent, dict) else parent.id)
    child_ids: List[str] = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        # ────────────────────── 1. create children ───────────────────
        for child in children:
            child_ids.append(str(child["id"]))
            req = {
                "jsonrpc": "2.0",
                "method": "Tasks.create",
                "params": child,
                "id": str(uuid.uuid4()),
            }
            await client.post(GATEWAY_URL, json=req)

        # ────────────────────── 2. update parent ─────────────────────
        patch_req = {
            "jsonrpc": "2.0",
            "method": "Tasks.update",
            "params": {
                "id": parent_id,
                # any additional updates can be embedded here
                "result": {"children": child_ids},
            },
            "id": str(uuid.uuid4()),
        }
        await client.post(GATEWAY_URL, json=patch_req)

        # ────────────────────── 3. finish parent ─────────────────────
        finished_req = {
            "jsonrpc": "2.0",
            "method": "Work.finished",
            "params": {
                "taskId": parent_id,
                "status": final_status.value,
                "result": result,
            },
            "id": str(uuid.uuid4()),
        }
        await client.post(GATEWAY_URL, json=finished_req)

    return {"children": child_ids, "_final_status": final_status.value}
