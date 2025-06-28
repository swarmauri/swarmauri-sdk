from __future__ import annotations

import uuid

from .. import READY_QUEUE, dispatcher, log, queue
from peagen.defaults import POOL_CREATE, POOL_JOIN, POOL_LIST_TASKS


@dispatcher.method(POOL_CREATE)
async def pool_create(name: str) -> dict:
    await queue.sadd("pools", name)
    log.info("pool created: %s", name)
    return {"name": name}


@dispatcher.method(POOL_JOIN)
async def pool_join(name: str) -> dict:
    member = str(uuid.uuid4())[:8]
    await queue.sadd(f"pool:{name}:members", member)
    log.info("member %s joined pool %s", member, name)
    return {"memberId": member}


@dispatcher.method(POOL_LIST_TASKS)
async def pool_list(
    poolName: str, limit: int | None = None, offset: int = 0
) -> list[dict]:
    """Return tasks queued for *poolName* with optional pagination."""
    start = max(offset, 0)
    end = -1 if limit is None else start + limit - 1
    ids = await queue.lrange(f"{READY_QUEUE}:{poolName}", start, end)
    tasks = []
    from peagen.schemas import TaskRead  # dynamic import to avoid circular

    for r in ids:
        t = TaskRead.model_validate_json(r)
        data = t.model_dump()
        if t.duration is not None:
            data["duration"] = t.duration
        tasks.append(data)
    return tasks
