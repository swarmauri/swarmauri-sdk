"""
gateway.hooks.pool
──────────────────────
Only CRUD hooks remain – no ad-hoc RPC methods.
"""

from __future__ import annotations

from typing import Any, Dict

from autoapi.v2 import AutoAPI, Phase

from peagen.orm import Pool

from peagen.gateway import api, log, queue

# Fast, cacheable access to the generated Pool schemas
PoolRead = AutoAPI.get_schema(Pool, "read")


# ─────────────────────────── CRUD hooks ────────────────────────────
@api.hook(Phase.PRE_TX_BEGIN, model="Pools", op="create")
async def pre_pool_create(ctx: Dict[str, Any]) -> None:
    """Stash the pool name so the post-hook can use it."""
    log.info("entering pre_pool_create")
    ctx["pool_name"] = ctx["env"].params.name


@api.hook(Phase.POST_COMMIT, model="Pools", op="create")
async def post_pool_create(ctx: Dict[str, Any]) -> None:
    """Register the new pool in Redis and shape the response."""
    log.info("entering post_pool_create")
    name = ctx["pool_name"]
    await queue.sadd("pools", name)
    log.info("pool created: %s", name)

    # Ensure the RPC result schema is exactly what AutoAPI advertises
    ctx["result"] = PoolRead(name=name).model_dump()
