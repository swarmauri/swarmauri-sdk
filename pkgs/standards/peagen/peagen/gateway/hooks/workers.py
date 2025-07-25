"""
gateway.api.hooks.workers
─────────────────────────
AutoAPI-native hooks for Worker CRUD.

• Worker.create   – pool registration & handler discovery
• Worker.update   – heartbeat (keep-alive) + mutable fields
• Worker.list     – DB result replaced with live-only snapshot
"""

from __future__ import annotations

import json
from typing import Dict, Mapping, Any
from pydantic import BaseModel

from autoapi.v2 import Phase, AutoAPI
from peagen.transport.jsonrpc import RPCException
from peagen.orm import Worker

from peagen.defaults import WORKER_KEY, WORKER_TTL
from peagen.gateway import log, queue, api
from peagen.gateway._publish import _publish_event

# ─────────────────── schema handles ────────────────────────────────────
WorkerCreate = AutoAPI.get_schema(Worker, "create")
WorkerRead = AutoAPI.get_schema(Worker, "read")
WorkerUpdate = AutoAPI.get_schema(Worker, "update")
WorkerListQ = AutoAPI.get_schema(Worker, "list")  # query model


def _as_redis_hash(model: BaseModel) -> Mapping[str, str]:
    """
    Convert a Pydantic model to a flat mapping[str, str] acceptable to HSET.
    • scalars → str(v)
    • dict / list → json.dumps(v, separators=(',', ':'))
    • None      → skipped (keeps hash compact)
    """
    out: dict[str, str] = {}
    for k, v in model.model_dump(mode="json").items():
        if v is None:
            continue
        if isinstance(v, (dict, list)):
            out[k] = json.dumps(v, separators=(",", ":"))
        else:
            out[k] = str(v)
    return out


# ─────────────────── 1. WORKERS.CREATE hooks ───────────────────────────
@api.hook(Phase.POST_RESPONSE, model="Worker", op="create")
async def post_worker_create_cache_pool(ctx: Dict[str, Any]) -> None:
    log.info("entering post_worker_create_cache_pool")

    created: WorkerRead = WorkerRead(**ctx["result"])
    log.info(f"worker {created.id} joined pool_id {created.pool_id}")

    # maintain a set of pool members for quick WS broadcasts
    try:
        await queue.sadd(f"pool_id:{created.pool_id}:members", str(created.id))
    except Exception as exc:
        log.error(f"failure to add member to pool queue. err: {exc}")


@api.hook(Phase.POST_RESPONSE, model="Worker", op="create")
async def post_worker_create_cache_worker(ctx: Dict[str, Any]) -> None:
    log.info("entering post_worker_create_cache_worker")

    created: WorkerRead = WorkerRead(**ctx["result"])
    log.info(f"worker {created.id} joined pool_id {created.pool_id}")

    try:
        key = WORKER_KEY.format(str(created.id))

        await queue.hset(key, _as_redis_hash(created))
        await queue.expire(key, WORKER_TTL)
        log.info(f"cached `{key}` ")
    except Exception as exc:
        log.error(f"failure to add worker. err: {exc}")

    try:
        await _publish_event(queue, "Worker.create", created)
    except Exception as exc:
        log.error(f"failure to _publish_event for: `Worker.create` err: {exc}")


# ─────────────────── 2. WORKERS.UPDATE hooks – heartbeat ───────────────
@api.hook(Phase.PRE_TX_BEGIN, model="Worker", op="update")
async def pre_worker_update(ctx: Dict[str, Any]) -> None:
    log.info("entering pre_worker_update")

    wu: WorkerUpdate = ctx["env"].params
    worker_id: str = str(wu["id"] or wu["item_id"])

    # pull any cached data; first heartbeat after restart may miss
    cached = await queue.exists(WORKER_KEY.format(worker_id))
    if not cached and wu["pool_id"] is None:
        raise RPCException(code=-32602, message="unknown worker; pool_id required")

    # store for downstream use
    ctx["worker_id"] = worker_id


@api.hook(Phase.POST_RESPONSE, model="Worker", op="update")
async def post_worker_update_cache_pool(ctx: Dict[str, Any]) -> None:
    log.info("entering post_worker_update_cache_pool")

    log.info("heartbeat stored for %s", str(ctx["worker_id"]))

    try:
        updated: WorkerRead = WorkerRead(**ctx["result"])
        worker_id: str = ctx["worker_id"]

        # keep pool id in its members-set so /ws metrics stay functional
        if updated.pool_id:
            await queue.sadd(f"pool_id:{updated.pool_id}:members", worker_id)
        log.info(f"cached member `{worker_id}` in `{updated.pool_id}`")
    except Exception as exc:
        log.info(
            f"pool member `{worker_id}` failed to cache in `{updated.pool_id}` err: {exc}"
        )


@api.hook(Phase.POST_RESPONSE, model="Worker", op="update")
async def post_worker_update_cache_worker(ctx: Dict[str, Any]) -> None:
    log.info("entering post_worker_update_cache_worker")
    try:
        updated: WorkerRead = WorkerRead(**ctx["result"])
        worker_id: str = ctx["worker_id"]

        log.info(f"\nupdated.model_dump_json(): {updated.model_dump_json()}\n")

        key = WORKER_KEY.format(worker_id)
        log.info(f"key: {key}")
        await queue.hset(key, {"updated_at": str(updated.updated_at)})
        log.info("key set worked.")
        await queue.expire(key, WORKER_TTL)
        log.info("key expiration set.")

        log.info(f"cached worker: `{worker_id}` ")
    except Exception as exc:
        log.info(f"cached failed for worker: `{worker_id}` err: {exc}")

    try:
        await _publish_event(queue, "Worker.update", updated)
    except Exception as exc:
        log.error(f"failure to _publish_event for: `Worker.update` err: {exc}")


# ─────────────────── 3. WORKERS.LIST post-hook ─────────────────────────
@api.hook(Phase.POST_HANDLER, model="Worker", op="list")
async def post_workers_list(ctx: Dict[str, Any]) -> None:
    """Replace DB snapshot with live-only snapshot if Redis has fresher info."""
    # For brevity this stays empty; implement when real-time pool state is required.
    log.info("entering post_workers_list")
    pass


@api.hook(Phase.POST_HANDLER, model="Worker", op="delete")
async def post_workers_delete(ctx: Dict[str, Any]) -> None:
    """Expire the worker's registry entry immediately."""
    try:
        wu: WorkerUpdate = ctx["env"].params
        worker_id: str = str(wu["id"] or wu["item_id"])
        await queue.expire(WORKER_KEY.format(worker_id), 0)

        log.info(f"worker expired: `{worker_id}` ")
    except Exception as exc:
        log.info(f"worker expiration op failed: `{worker_id} `err: {exc}")

    try:
        await _publish_event(queue, "Worker.delete", {"id": worker_id})
    except Exception as exc:
        log.info(f"failure to _publish_event for: `Worker.delete` err: {exc}")
