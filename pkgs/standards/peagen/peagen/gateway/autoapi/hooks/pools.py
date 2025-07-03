"""
AutoAPI hooks for pool-related operations.
"""

import uuid
from typing import Any, Dict

from ... import (
    READY_QUEUE,
    log,
    queue,
)
from ...autoapi import api

# ---------------------- Pool Hooks ----------------------


@api.hook(api.Phase.PRE_TX_BEGIN, method="pools.create")
async def pre_pool_create(ctx: Dict[str, Any]) -> None:
    """Pre-processing for pool creation"""
    params = ctx.get("env").params

    # Store the pool name for logging
    ctx["pool_name"] = params.get("name")


@api.hook(api.Phase.POST_COMMIT, method="pools.create")
async def post_pool_create(ctx: Dict[str, Any]) -> None:
    """Post-commit operations for pool creation"""
    result = ctx.get("result")
    pool_name = ctx.get("pool_name")

    if not result or not pool_name:
        return

    # Register pool in Redis
    await queue.sadd("pools", pool_name)

    # Format response to match original API
    ctx["result"] = {"name": pool_name}

    # Log pool creation
    log.info("pool created: %s", pool_name)


@api.hook(api.Phase.PRE_TX_BEGIN, method="pools.join")
async def pre_pool_join(ctx: Dict[str, Any]) -> None:
    """Pre-processing for pool joining"""
    params = ctx.get("env").params

    # Store the pool name
    ctx["pool_name"] = params.get("name")

    # Generate a member ID if not provided
    member_id = params.get("memberId") or str(uuid.uuid4())[:8]
    params["memberId"] = member_id
    ctx["member_id"] = member_id


@api.hook(api.Phase.POST_COMMIT, method="pools.join")
async def post_pool_join(ctx: Dict[str, Any]) -> None:
    """Post-commit operations for pool joining"""
    result = ctx.get("result")
    pool_name = ctx.get("pool_name")
    member_id = ctx.get("member_id")

    if not result or not pool_name or not member_id:
        return

    # Add member to pool in Redis
    await queue.sadd(f"pool:{pool_name}:members", member_id)

    # Format response to match original API
    ctx["result"] = {"memberId": member_id}

    # Log member joining
    log.info("member %s joined pool %s", member_id, pool_name)


@api.hook(api.Phase.PRE_TX_BEGIN, method="pools.list_tasks")
async def pre_pool_list_tasks(ctx: Dict[str, Any]) -> None:
    """Pre-processing for pool task listing"""
    params = ctx.get("env").params

    # Store parameters for later
    ctx["pool_name"] = params.get("poolName")
    ctx["limit"] = params.get("limit")
    ctx["offset"] = params.get("offset", 0)


@api.hook(api.Phase.POST_HANDLER, method="pools.list_tasks")
async def post_pool_list_tasks(ctx: Dict[str, Any]) -> None:
    """Post-handler operations for pool task listing"""
    # Skip if no context or result is already set
    if "result" in ctx:
        return

    pool_name = ctx.get("pool_name")
    limit = ctx.get("limit")
    offset = ctx.get("offset", 0)

    if not pool_name:
        ctx["result"] = {"tasks": []}
        return

    # Pagination parameters
    start = max(offset, 0)
    end = -1 if limit is None else start + limit - 1

    # Get tasks from Redis
    ids = await queue.lrange(f"{READY_QUEUE}:{pool_name}", start, end)
    tasks = []

    # Process each task
    from peagen.orm.schemas import (
        TaskRead,  # Import here to avoid circular dependencies
    )

    for r in ids:
        try:
            t = TaskRead.model_validate_json(r)
            data = t.model_dump()
            if t.duration is not None:
                data["duration"] = t.duration
            tasks.append(data)
        except Exception as e:
            log.warning(f"Error parsing task from Redis: {e}")

    # Format response to match original API
    ctx["result"] = {"tasks": tasks}
