from __future__ import annotations

import time
import json

import httpx

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

from peagen.transport.jsonrpc_schemas import Status
from peagen.transport.jsonrpc import RPCException
from peagen.transport.jsonrpc_schemas.work import (
    WORK_FINISHED,
    FinishedParams,
    FinishedResult,
)
from peagen.transport.jsonrpc_schemas.worker import (
    WORKER_REGISTER,
    WORKER_HEARTBEAT,
    WORKER_LIST,
    RegisterParams,
    RegisterResult,
    HeartbeatParams,
    HeartbeatResult,
    ListParams,
    ListResult,
    WorkerInfo,
)


@dispatcher.method(WORKER_REGISTER)
async def worker_register(params: RegisterParams) -> dict:
    """Register a worker and persist its advertised handlers."""

    workerId = params.workerId
    pool = params.pool
    url = params.url
    advertises = params.advertises
    handlers = params.handlers

    handler_list: list[str] = handlers or []
    if not handler_list:
        well_known_url = url.replace("/rpc", "/well-known")
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(well_known_url)
                if resp.status_code == 200:
                    handler_list = resp.json().get("handlers", [])
        except Exception as exc:  # noqa: BLE001
            log.warning("/well-known fetch failed for %s: %s", workerId, exc)

    if not handler_list:
        raise RPCException(code=-32602, message="worker supports no handlers")

    await _upsert_worker(
        workerId,
        {
            "pool": pool,
            "url": url,
            "advertises": advertises,
            "handlers": handler_list,
        },
    )
    log.info("worker %s registered (%s) handlers=%s", workerId, pool, handler_list)
    return RegisterResult(ok=True).model_dump()


@dispatcher.method(WORKER_HEARTBEAT)
async def worker_heartbeat(params: HeartbeatParams) -> dict:
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


@dispatcher.method(WORKER_LIST)
async def worker_list(params: ListParams) -> dict:
    """Return active workers, optionally filtered by *pool*."""

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
    return ListResult([WorkerInfo(**w) for w in workers]).model_dump()


@dispatcher.method(WORK_FINISHED)
async def work_finished(params: FinishedParams) -> dict:
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
    started = t.get("started_at")
    if status == "running" and started is None:
        t["started_at"] = now
    elif Status.is_terminal(status):
        if started is None:
            t["started_at"] = now
        t["finished_at"] = now

    await _save_task(t)
    await _persist(t)
    await _publish_task(t)
    if Status.is_terminal(status):
        await _finalize_parent_tasks(taskId)

    log.info("task %s completed: %s", taskId, status)
    return FinishedResult(ok=True).model_dump()
