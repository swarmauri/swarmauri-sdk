from __future__ import annotations

import uuid
from typing import Any, Dict

from autoapi.v2 import Phase

from peagen.transport.jsonrpc_schemas.pool import (
    POOL_JOIN,
    POOL_LIST_TASKS,
    CreateResult,
    JoinParams,
    JoinResult,
    ListParams,
    ListResult,
)

from .. import READY_QUEUE, dispatcher, log, queue
from . import api

# ------------------------------------------------------------------------
# Pool CRUD operation hooks
# ------------------------------------------------------------------------


@api.hook(Phase.PRE_TX_BEGIN, method="pools.create")
async def pre_pool_create(ctx: Dict[str, Any]) -> None:
    """Pre-hook for pool creation: Extract and validate name."""
    params = ctx["env"].params
    name = params.name

    # Store pool name for post-commit hook
    ctx["pool_name"] = name


@api.hook(Phase.POST_COMMIT, method="pools.create")
async def post_pool_create(ctx: Dict[str, Any]) -> None:
    """Post-hook for pool creation: Register in Redis."""
    name = ctx["pool_name"]

    # Register the pool in Redis
    await queue.sadd("pools", name)

    log.info("pool created: %s", name)

    # Set response format
    ctx["result"] = CreateResult(name=name).model_dump()


# ------------------------------------------------------------------------
# Custom operations that don't map directly to CRUD
# ------------------------------------------------------------------------


@dispatcher.method(POOL_JOIN)
async def pool_join(params: JoinParams) -> dict:
    """Join a worker to a pool."""
    name = params.name
    member = str(uuid.uuid4())[:8]
    await queue.sadd(f"pool:{name}:members", member)
    log.info("member %s joined pool %s", member, name)
    return JoinResult(memberId=member).model_dump()


@dispatcher.method(POOL_LIST_TASKS)
async def pool_list(params: ListParams) -> dict:
    """Return tasks queued for *poolName* with optional pagination."""
    poolName = params.poolName
    limit = params.limit
    offset = params.offset

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
