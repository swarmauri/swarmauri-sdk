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
from typing import Any, Dict, List

from autoapi.v2 import Phase, AutoAPI
from peagen.transport.jsonrpc import RPCException
from peagen.orm import Worker

from peagen.defaults import WORKER_KEY, WORKER_TTL, READY_QUEUE
from .. import log, queue, api
from ..schedule_helpers import _load_task, _save_task, _finalize_parent_tasks
from .._publish import _publish_task, _publish_event, _publish_queue_length

# ─────────────────── schema handles ────────────────────────────────────
WorkerCreate = AutoAPI.get_schema(Worker, "create")
WorkerRead = AutoAPI.get_schema(Worker, "read")
WorkerUpdate = AutoAPI.get_schema(Worker, "update")  # NEW
WorkersListQ = AutoAPI.get_schema(Worker, "list")  # request model


# ─────────────────── 1. WORKERS.CREATE hooks ───────────────────────────
@api.hook(Phase.PRE_TX_BEGIN, method="Workers.create")
async def pre_worker_create(ctx: Dict[str, Any]) -> None:
    wc: WorkerCreate = ctx["env"].params

    # auto-discover handlers if caller omitted them
    handlers = wc.handlers or []
    if not handlers:
        try:
            well_known = wc.url.replace("/rpc", "/well-known")
            async with httpx.AsyncClient(timeout=5) as cl:
                r = await cl.get(well_known)
                if r.status_code == 200:
                    handlers = r.json().get("handlers", [])
        except Exception as exc:  # noqa: BLE001
            log.warning("well-known fetch for %s failed – %s", wc.url, exc)

    if not handlers:
        raise RPCException(code=-32602, message="worker supports no handlers")

    ctx["worker_in"] = wc.model_copy(update={"handlers": handlers})


@api.hook(Phase.POST_COMMIT, method="Workers.create")
async def post_worker_create(ctx: Dict[str, Any]) -> None:
    created: WorkerRead = ctx["result"]
    wc: WorkerCreate = ctx["worker_in"]

    await _cache_worker(
        created.id,
        {
            "pool": wc.pool,
            "url": wc.url,
            "advertises": wc.advertises or {},
            "handlers": wc.handlers,
        },
    )
    await queue.sadd(f"pool:{wc.pool}:members", created.id)
    log.info("worker %s joined pool %s", created.id, wc.pool)


# ─────────────────── 2. WORKERS.UPDATE hooks – heartbeat ───────────────
@api.hook(Phase.PRE_TX_BEGIN, method="Workers.update")
async def pre_worker_update(ctx: Dict[str, Any]) -> None:
    wu: WorkerUpdate = ctx["env"].params
    wid = wu.id or wu.item_id

    # Pull existing cached data (may not exist for first heartbeat after restart)
    cached = await queue.hgetall(WORKER_KEY.format(wid))
    if not cached and (wu.pool is None or wu.url is None):
        raise RPCException(code=-32602, message="unknown worker; pool & url required")

    # merge incoming changes
    mutated = {
        "pool": wu.pool if wu.pool is not None else cached.get("pool"),
        "url": wu.url if wu.url is not None else cached.get("url"),
        "advertises": wu.advertises or cached.get("advertises", {}),
        "handlers": wu.handlers or cached.get("handlers", []),
    }
    ctx["worker_cache_upd"] = mutated
    ctx["worker_id"] = wid


@api.hook(Phase.POST_COMMIT, method="Workers.update")
async def post_worker_update(ctx: Dict[str, Any]) -> None:
    wid = ctx["worker_id"]
    data = ctx["worker_cache_upd"]

    await _cache_worker(wid, data)
    log.debug("heartbeat stored for %s", wid)


# ─────────────────── 3. WORKERS.LIST post-hook ─────────────────────────
@api.hook(Phase.POST_HANDLER, method="Workers.list")
async def post_workers_list(ctx: Dict[str, Any]) -> None:
    params = ctx["env"].params or {}
    filter_pool = params.get("pool")

    keys = await queue.keys("worker:*")
    now = int(time.time())
    result: List[Dict[str, Any]] = []

    for k in keys:
        blob = await queue.hgetall(k)
        if not blob:
            continue
        if now - int(blob.get("last_seen", 0)) > WORKER_TTL:
            continue
        if filter_pool and blob.get("pool") != filter_pool:
            continue

        advert = (
            json.loads(blob["advertises"])
            if isinstance(blob.get("advertises"), str)
            else blob.get("advertises", {})
        )
        handlers = (
            json.loads(blob["handlers"])
            if isinstance(blob.get("handlers"), str)
            else blob.get("handlers", [])
        )

        result.append(
            {
                "id": k.split(":", 1)[1],
                "pool": blob.get("pool"),
                "url": blob.get("url"),
                "advertises": advert,
                "handlers": handlers,
                "last_seen": int(blob["last_seen"]),
            }
        )

    ctx["result"] = result


# ─────────────────── Redis helper ──────────────────────────────────────
async def _cache_worker(worker_id: str, data: dict) -> None:
    """
    Upsert worker metadata in `worker:<id>` hash and refresh TTL.
    """
    key = WORKER_KEY.format(worker_id)
    now = int(time.time())

    # serialise nested structures consistently
    mapping = {
        "pool": data.get("pool"),
        "url": data.get("url"),
        "advertises": json.dumps(data.get("advertises", {})),
        "handlers": json.dumps(data.get("handlers", [])),
        "last_seen": now,
    }

    await queue.hset(key, mapping=mapping)
    await queue.expire(key, WORKER_TTL)

    # keep pool name in the set → queue length WS updates stay functional
    if data.get("pool"):
        await queue.sadd("pools", data["pool"])

    await _publish_event("worker.update", {"id": worker_id, **data})
