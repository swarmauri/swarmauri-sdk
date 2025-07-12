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
@api.hook(Phase.POST_RESPONSE, method="Workers.create")
async def post_worker_create(ctx: Dict[str, Any]) -> None:
    log.info("entering post_worker_create")

    created: WorkerRead = WorkerRead(**ctx["result"])
    log.info(f"worker {created.id} joined pool_id {created.pool_id}")

    # maintain a set of pool members for quick WS broadcasts
    try:
        await queue.sadd(f"pool_id:{created.pool_id}:members", str(created.id))
    except Exception as exc:
        log.error(f"failure to add member to pool queue.", 'err: {exc}')

    try:
        key = WORKER_KEY.format(str(created.id))
        await queue.set(key, created.model_dump_json())
        await queue.expire(key, WORKER_TTL)
        log.info(f"cached `{key}` ")
    except Exception as exc:
        log.error(f"failure to add worker. err: {exc}")


    try:
        await _publish_event(queue, "Workers.create", created)
    except:
        log.error("post_worker_create failure to _publish_event for: `Workers.create`")




# ─────────────────── 2. WORKERS.UPDATE hooks – heartbeat ───────────────
@api.hook(Phase.PRE_TX_BEGIN, method="Workers.update")
async def pre_worker_update(ctx: Dict[str, Any]) -> None:
    log.info("entering pre_worker_update")

    wu: WorkerUpdate = ctx["env"].params
    worker_id: str   = str(wu['id'] or wu['item_id'])

    # pull any cached data; first heartbeat after restart may miss
    cached = await queue.get(WORKER_KEY.format(worker_id))
    if not cached and wu['pool_id'] is None:
        raise RPCException(code=-32602, message="unknown worker; pool_id required")

    # store for downstream use
    ctx["worker_id"]          = worker_id


@api.hook(Phase.POST_RESPONSE, method="Workers.update")
async def post_worker_update_cache_pool(ctx: Dict[str, Any]) -> None:
    log.info("entering post_worker_update_cache_pool")

    log.info("heartbeat stored for %s", str(ctx['worker_id']))

    try:
        updated: WorkerRead = WorkerRead(**ctx["result"])
        worker_id: str      = ctx["worker_id"]

        # keep pool id in its members-set so /ws metrics stay functional
        if updated.pool_id:
            await queue.sadd(f"pool_id:{updated.pool_id}:members", worker_id)
        log.info(f"cached member `{worker_id}` in `{updated.pool_id}`")
    except Exception as exc:
        log.info(f"pool member `{worker_id}` failed to cache in `{updated.pool_id}` err: {exc}")


@api.hook(Phase.POST_RESPONSE, method="Workers.update")
async def post_worker_update_cache_worker(ctx: Dict[str, Any]) -> None:
    log.info("entering post_worker_update_cache_worker")
    try:
        updated: WorkerRead = WorkerRead(**ctx["result"])
        worker_id: str      = ctx["worker_id"]

        log.info(f"\nupdated.model_dump_json(): {updated.model_dump_json()}\n")


        key = WORKER_KEY.format(worker_id)
        log.info(f"key: {key}")
        await queue.set(key, updated.model_dump_json())
        log.info(f"key set worked.")
        await queue.expire(key, WORKER_TTL)
        log.info(f"key expiration set.")

        log.info(f"cached worker: `{worker_id}` ")
    except Exception as exc:
        log.info(f"cached failed for worker: `{worker_id}` err: {exc}")

    try:
        await _publish_event(queue, "Workers.update", updated)
    except Exception as exc:
        log.error(f"post_worker_update failure to _publish_event for: `Workers.update` err: {exc}")

# ─────────────────── 3. WORKERS.LIST post-hook ─────────────────────────
@api.hook(Phase.POST_HANDLER, method="Workers.list")
async def post_workers_list(ctx: Dict[str, Any]) -> None:
    """Replace DB snapshot with live-only snapshot if Redis has fresher info."""
    # For brevity this stays empty; implement when real-time pool state is required.
    log.info("entering post_workers_list")
    pass

@api.hook(Phase.POST_HANDLER, method="Workers.delete")
async def post_workers_delete(ctx: Dict[str, Any]) -> None:
    """Expire the worker's registry entry immediately."""
    try:
        wu: WorkerUpdate = ctx["env"].params
        worker_id: str   = str(wu['id'] or wu['item_id'])
        await queue.expire(WORKER_KEY.format(worker_id), 0)

        log.info(f"worker expired: `{worker_id}` ")
    except Exception as exc:
        log.info(f"worker expiration op failed: `{worker_id} `err: {exc}")

    try:
        await _publish_event(queue, "Workers.delete", {"id": worker_id})
    except Exception as exc:
        log.info(f"publish event for Workers.delete failed on : `{worker_id}` err: {exc}")
