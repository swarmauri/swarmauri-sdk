from __future__ import annotations

import uuid

from .. import READY_QUEUE, dispatcher, log, queue
from peagen.protocols.methods.pool import (
    POOL_CREATE,
    POOL_JOIN,
    POOL_LIST_TASKS,
    CreateParams,
    CreateResult,
    JoinParams,
    JoinResult,
    ListParams,
    ListResult,
)


@dispatcher.method(POOL_CREATE)
async def pool_create(params: CreateParams) -> dict:
    name = params.name
    await queue.sadd("pools", name)
    log.info("pool created: %s", name)
    return CreateResult(name=name).model_dump()


@dispatcher.method(POOL_JOIN)
async def pool_join(params: JoinParams) -> dict:
    name = params.name
    member = str(uuid.uuid4())[:8]
    await queue.sadd(f"pool:{name}:members", member)
    log.info("member %s joined pool %s", member, name)
    return JoinResult(memberId=member).model_dump()


@dispatcher.method(POOL_LIST_TASKS)
async def pool_list(params: ListParams) -> dict:
    poolName = params.poolName
    limit = params.limit
    offset = params.offset
    """Return tasks queued for *poolName* with optional pagination."""
    start = max(offset, 0)
    end = -1 if limit is None else start + limit - 1
    ids = await queue.lrange(f"{READY_QUEUE}:{poolName}", start, end)
    tasks = []
    from peagen.orm.schemas import TaskRead  # dynamic import to avoid circular

    for r in ids:
        t = TaskRead.model_validate_json(r)
        data = t.model_dump()
        if t.duration is not None:
            data["duration"] = t.duration
        tasks.append(data)
    return ListResult(tasks).model_dump()
