"""
gateway._publish
────────────────
Utilities that fan-out events over Redis Pub/Sub.

Changes:
• _publish_task() now works with Pydantic models (TaskRead / TaskCreate)
  rather than ad-hoc TaskBlob dicts.
"""

from __future__ import annotations

import json
import time
from typing import Any, Mapping

# from . import queue, log                           # queue is an aioredis wrapper
from peagen.defaults import PUBSUB_CHANNEL, READY_QUEUE


# ------------------------------------------------------------------ #
# 1. low-level publish helper (unchanged)
# ------------------------------------------------------------------ #
async def _publish_event(queue, event_type: str, data_obj: Any) -> None:
    try:
        data = _to_serialisable(data_obj).copy()

        event = {
            "type": event_type,
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "data": data,
        }
        await queue.publish(PUBSUB_CHANNEL, json.dumps(event, default=str))
    except Exception as exc:
        print(f"_publish_event failed: {exc}")
        raise exc


# ------------------------------------------------------------------ #
# 2. broadcast a single task update  (schema-aware)
# ------------------------------------------------------------------ #
def _to_serialisable(obj: Any) -> Mapping[str, Any]:
    """
    Normalise *obj* into a plain dict suitable for JSON encoding.
    • Pydantic models → model_dump(mode="json")
    • dicts → returned unchanged
    • anything else → raises TypeError
    """
    from pydantic import BaseModel

    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    if isinstance(obj, dict):
        return obj
    raise TypeError(f"unsupported task payload type: {type(obj)}")


async def _publish_task(task_obj: Any) -> None:
    """
    Publish `task.update` for *task_obj* (TaskRead / TaskCreate / dict).

    Adds the `duration` key only when it exists and is not None.
    """
    data = _to_serialisable(task_obj).copy()

    # Optional duration propagation (if the column exists in TaskRead)
    duration = getattr(task_obj, "duration", None)
    if duration is not None:
        data["duration"] = duration

    await _publish_event("task.update", data)


# ------------------------------------------------------------------ #
# 3. queue length helper (unchanged)
# ------------------------------------------------------------------ #
async def _publish_queue_length(queue, pool: str) -> None:
    qlen = await queue.llen(f"{READY_QUEUE}:{pool}")
    await _publish_event("queue.update", {"pool": pool, "length": qlen})
