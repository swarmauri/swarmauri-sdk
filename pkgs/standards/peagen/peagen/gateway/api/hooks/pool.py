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

