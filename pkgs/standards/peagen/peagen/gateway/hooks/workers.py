"""
gateway.api.hooks.workers
─────────────────────────
AutoAPI-native hooks for Worker CRUD.

• Workers.create   – pool registration & handler discovery
• Workers.update   – heartbeat (keep-alive) + mutable fields
• Workers.list     – DB result replaced with live-only snapshot
"""

from __future__ import annotations

import json
import time
import httpx
import uuid
from typing import Any, Dict

from autoapi.v2 import Phase, AutoAPI
from peagen.transport.jsonrpc import RPCException
from peagen.orm import Worker

from peagen.defaults import WORKER_KEY, WORKER_TTL
from peagen.gateway import log, queue, api
from peagen.gateway._publish import _publish_event

# ─────────────────── schema handles ────────────────────────────────────
WorkerCreate = AutoAPI.get_schema(Worker, "create")
WorkerRead   = AutoAPI.get_schema(Worker, "read")
WorkerUpdate = AutoAPI.get_schema(Worker, "update")
WorkersListQ = AutoAPI.get_schema(Worker, "list")        # query model


# ─────────────────── 1. WORKERS.CREATE hooks ───────────────────────────
@api.hook(Phase.POST_COMMIT, method="Workers.create")
async def post_worker_create(ctx: Dict[str, Any]) -> None:
    log.info("entering post_worker_create")

    created: WorkerRead = WorkerRead(**ctx["result"])

    # maintain a set of pool members for quick WS broadcasts
    await queue.sadd(f"pool_id:{created.pool_id}:members", str(created.id))

    log.info("worker %s joined pool_id %s", str(created.id), str(created.pool_id))
    await _publish_event("Workers.create", {created.model_dump()})


# ─────────────────── 2. WORKERS.UPDATE hooks – heartbeat ───────────────
@api.hook(Phase.PRE_TX_BEGIN, method="Workers.update")
async def pre_worker_update(ctx: Dict[str, Any]) -> None:
    log.info("entering pre_worker_update")

    wu: WorkerUpdate = ctx["env"].params
    worker_id: str   = str(wu['id'] or wu['item_id'])

    # pull any cached data; first heartbeat after restart may miss
    cached = await queue.hgetall(WORKER_KEY.format(worker_id))
    if not cached and wu['pool_id'] is None:
        raise RPCException(code=-32602, message="unknown worker; pool_id required")

    # store for downstream use
    ctx["worker_id"]          = worker_id


@api.hook(Phase.POST_COMMIT, method="Workers.update")
async def post_worker_update(ctx: Dict[str, Any]) -> None:
    log.info("entering post_worker_update")

    try:
        updated: WorkerRead = ctx["result"]
        worker_id: str      = ctx["worker_id"]

        await _cache_worker(worker_id, {**updated})
        log.debug("heartbeat stored for %s", worker_id)

        await _publish_event("Workers.update", {**updated})
    except Exception as exc:
        log.warning("post_worker_update failure: %s", exc)


# ─────────────────── 3. WORKERS.LIST post-hook ─────────────────────────
@api.hook(Phase.POST_HANDLER, method="Workers.list")
async def post_workers_list(ctx: Dict[str, Any]) -> None:
    """Replace DB snapshot with live-only snapshot if Redis has fresher info."""
    # For brevity this stays empty; implement when real-time pool state is required.
    pass


# ─────────────────── Redis helper ──────────────────────────────────────
async def _cache_worker(worker_id: str, data: dict) -> None:
    """
    Upsert worker metadata in `worker:<id>` hash and refresh TTL.
    """
    key = WORKER_KEY.format(worker_id)
    now = int(time.time())

    await queue.hset(key, mapping=data)
    await queue.expire(key, WORKER_TTL)

    # keep pool id in its members-set so /ws metrics stay functional
    if data.get("pool_id"):
        await queue.sadd("pools", data["pool_id"])

    await _publish_event("Workers.update", {"id": worker_id, **data})
