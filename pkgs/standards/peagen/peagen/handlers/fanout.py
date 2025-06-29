from __future__ import annotations

import os
import uuid
from typing import Iterable, List, Dict, Any

import httpx

from peagen.protocols.methods.task import PatchResult
from peagen.orm.status import Status
from peagen.protocols import Request as RPCEnvelope
from peagen.protocols.methods import TASK_SUBMIT, TASK_PATCH
from peagen.protocols.methods.task import PatchParams
from . import ensure_task


async def fan_out(
    parent: PatchResult | Dict[str, Any],
    children: Iterable[PatchResult],
    *,
    result: Dict[str, Any] | None = None,
    final_status: Status = Status.waiting,
) -> Dict[str, Any]:
    """Submit *children* and update *parent* with their IDs."""
    gateway = os.getenv("DQ_GATEWAY", "http://localhost:8000/rpc")
    canonical_parent = ensure_task(parent)
    parent_id = str(canonical_parent.id)

    child_ids: List[str] = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for child in children:
            req = RPCEnvelope(
                id=str(uuid.uuid4()),
                method=TASK_SUBMIT,
                params={
                    "taskId": str(child.id),
                    "pool": child.pool,
                    "payload": child.payload,
                },
            ).model_dump(mode="json")
            await client.post(gateway, json=req)
            child_ids.append(str(child.id))

        patch = RPCEnvelope(
            id=str(uuid.uuid4()),
            method=TASK_PATCH,
            params=PatchParams(
                taskId=parent_id,
                changes={"result": {"children": child_ids}},
            ).model_dump(mode="json"),
        ).model_dump(mode="json")
        await client.post(gateway, json=patch)

        finish = RPCEnvelope(
            id=str(uuid.uuid4()),
            method="Work.finished",
            params={
                "taskId": str(parent_id),
                "status": final_status.value,
                "result": result,
            },
        ).model_dump(mode="json")
        await client.post(gateway, json=finish)

    return {"children": child_ids, "_final_status": final_status.value}
