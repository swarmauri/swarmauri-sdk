from __future__ import annotations

import json
import time
from typing import Any, Dict

import httpx
from autoapi.v2 import Phase

from peagen.transport.jsonrpc import RPCException
from peagen.transport.jsonrpc_schemas import Status
from peagen.transport.jsonrpc_schemas.work import (
    WORK_FINISHED,
    FinishedParams,
    FinishedResult,
)
from peagen.transport.jsonrpc_schemas.worker import (
    WORKER_HEARTBEAT,
    HeartbeatParams,
    HeartbeatResult,
    ListResult,
    RegisterResult,
    WorkerInfo,
)

from .. import (
    WORKER_KEY,
    WORKER_TTL,
    _finalize_parent_tasks,
    _load_task,
    _persist,
    _publish_task,
    _save_task,
    _upsert_worker,
    dispatcher,
    log,
    queue,
)
from . import api

# ------------------------------------------------------------------------
# Worker CRUD operation hooks
# ------------------------------------------------------------------------


@api.hook(Phase.PRE_TX_BEGIN, method="workers:register")
async def pre_worker_register(ctx: Dict[str, Any]) -> None:
    """Pre-hook for worker registration: Fetch handler list."""
    params = ctx["env"].params

    workerId = params.workerId
    pool = params.pool
    url = params.url
    advertises = params.advertises
    handlers = params.handlers

    handler_list = handlers or []
    if not handler_list:
        well_known_url = url.replace("/rpc", "/well-known")
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(well_known_url)
                if resp.status_code == 200:
                    handler_list = resp.json().get("handlers", [])
        except Exception as exc:
            log.warning("/well-known fetch failed for %s: %s", workerId, exc)

    if not handler_list:
        raise RPCException(code=-32602, message="worker supports no handlers")

    # Store data in context for use in later hooks
    ctx["worker_data"] = {
        "workerId": workerId,
        "pool": pool,
        "url": url,
        "advertises": advertises,
        "handlers": handler_list,
    }


@api.hook(Phase.POST_COMMIT, method="workers.create")
async def post_worker_register(ctx: Dict[str, Any]) -> None:
    """Post-hook for worker registration: Register in Redis."""
    worker_data = ctx["worker_data"]
    workerId = worker_data["workerId"]

    await _upsert_worker(
        workerId,
        {
            "pool": worker_data["pool"],
            "url": worker_data["url"],
            "advertises": worker_data["advertises"],
            "handlers": worker_data["handlers"],
        },
    )

    log.info(
        "worker %s registered (%s) handlers=%s",
        workerId,
        worker_data["pool"],
        worker_data["handlers"],
    )

    # Set response format
    ctx["result"] = RegisterResult(ok=True).model_dump()


@api.hook(Phase.POST_HANDLER, method="workers.list")
async def post_workers_list(ctx: Dict[str, Any]) -> None:
    """Post-hook for worker list: Return filtered list of workers."""
    params = ctx["env"].params
    pool = params.pool

    keys = await queue.keys("worker:*")
    workers = []
    now = int(time.time())

    for key in keys:
        w = await queue.hgetall(key)
        if not w:
            continue
        if now - int(w.get("last_seen", 0)) > WORKER_TTL:
            continue
        if pool and w.get("pool") != pool:
            continue

        # decode json-encoded fields
        advertises = w.get("advertises")
        if isinstance(advertises, str):
            try:
                advertises = json.loads(advertises)
            except Exception:
                advertises = {}

        handlers = w.get("handlers")
        if isinstance(handlers, str):
            try:
                handlers = json.loads(handlers)
            except Exception:
                handlers = []

        worker_info = {
            "id": key.split(":", 1)[1],
            **{k: v for k, v in w.items()},
            "advertises": advertises,
            "handlers": handlers,
        }
        workers.append(worker_info)

    ctx["result"] = ListResult([WorkerInfo(**w) for w in workers]).model_dump()


# ------------------------------------------------------------------------
# Custom operations that don't map directly to CRUD
# ------------------------------------------------------------------------


@dispatcher.method(WORKER_HEARTBEAT)
async def worker_heartbeat(params: HeartbeatParams) -> dict:
    """Update worker's last_seen timestamp to indicate it's still alive."""
    workerId = params.workerId
    # metrics are currently ignored
    pool = params.pool
    url = params.url

    known = await queue.exists(WORKER_KEY.format(workerId))
    if not known and not (pool and url):
        log.warning(
            "heartbeat from %s ignored: gateway lacks metadata; send pool+url or re-register",
            workerId,
        )
        return {"ok": False}

    mapping = {"last_seen": int(time.time())}
    if pool:
        mapping["pool"] = pool
    if url:
        mapping["url"] = url
    await queue.hset(WORKER_KEY.format(workerId), mapping=mapping)
    await queue.expire(WORKER_KEY.format(workerId), WORKER_TTL)
    return HeartbeatResult(ok=True).model_dump()


@dispatcher.method(WORK_FINISHED)
async def work_finished(params: FinishedParams) -> dict:
    """Update task status and result when a worker has finished processing."""
    taskId = params.taskId
    status = params.status
    result = params.result
    t = await _load_task(taskId)
    if not t:
        log.warning("Work.finished for unknown task %s", taskId)
        return {"ok": False}

    t["status"] = Status(status)
    t["result"] = result
    now = time.time()
    started = t.get("date_created")
    if status == "running" and started is None:
        t["date_created"] = now
        t["last_modified"] = now
    elif Status.is_terminal(status):
        if started is None:
            t["date_created"] = now
        t["last_modified"] = now

    await _save_task(t)
    await _persist(t)
    await _publish_task(t)
    if Status.is_terminal(status):
        await _finalize_parent_tasks(taskId)

    log.info("task %s completed: %s", taskId, status)
    return FinishedResult(ok=True).model_dump()


# ─────────────────────────── Workers ────────────────────────────
# workers are stored as hashes:  queue.hset worker:<id> pool url advertises last_seen
WORKER_KEY = "worker:{}"  # format with workerId
WORKER_TTL = 15  # seconds before a worker is considered dead
TASK_TTL = 24 * 3600  # 24 h, adjust as needed


# ─────────────────────────── IP tracking ─────────────────────────

async def _upsert_worker(workerId: str, data: dict) -> None:
    """
    Persist worker metadata in Redis hash `worker:<id>`.
    • Any value that isn't bytes/str/int/float is json-encoded.
    • last_seen is stored as Unix epoch seconds.
    """
    key = WORKER_KEY.format(workerId)
    existing = await queue.hgetall(key)
    for field in ("advertises", "handlers"):
        if field not in data and field in existing:
            try:
                data[field] = json.loads(existing[field])
            except Exception:  # noqa: BLE001
                data[field] = existing[field]

    coerced = {}
    for k, v in data.items():
        if isinstance(v, (bytes, str, int, float)):
            coerced[k] = v
        else:
            coerced[k] = json.dumps(v)  # serialize nested dicts, lists, etc.

    coerced["last_seen"] = int(time.time())  # heartbeat timestamp
    await queue.hset(key, mapping=coerced)
    await queue.expire(key, WORKER_TTL)  # <<—— TTL refresh
    # ensure the worker's pool is tracked so WebSocket clients
    # receive queue length updates even before a task is submitted
    pool = data.get("pool")
    if pool:
        await queue.sadd("pools", pool)
    await _publish_event("worker.update", {"id": workerId, **data})


async def _publish_queue_length(pool: str) -> None:
    qlen = len(await queue.lrange(f"{READY_QUEUE}:{pool}", 0, -1))
    await _publish_event("queue.update", {"pool": pool, "length": qlen})


async def _remove_worker(workerId: str) -> None:
    """Expire the worker's registry entry immediately."""
    await queue.expire(WORKER_KEY.format(workerId), 0)
    await _publish_event("worker.update", {"id": workerId, "removed": True})


async def _live_workers_by_pool(pool: str) -> list[dict]:
    keys = await queue.keys("worker:*")
    workers = []
    now = int(time.time())
    for k in keys:
        w = await queue.hgetall(k)
        if not w:  # TTL expired or never registered
            continue
        if now - int(w["last_seen"]) > WORKER_TTL:
            continue  # stale
        if w["pool"] == pool:
            wid = k.split(":", 1)[1]
            workers.append({"id": wid, **w})
    return workers


def _pick_worker(workers: list[dict], action: str | None) -> dict | None:
    """Return the first worker that advertises *action*."""
    if action is None:
        return None
    for w in workers:
        raw = w.get("handlers", [])
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:  # noqa: BLE001
                raw = []
        if action in raw:
            return w
    return None
