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

from peagen.orm.status import Status
from peagen.transport.jsonrpc import RPCException
from peagen.protocols.methods.worker import (
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
from peagen.defaults import WORK_FINISHED


@dispatcher.method(WORKER_REGISTER)
async def worker_register(params: RegisterParams) -> dict:
    """Register a worker and persist its advertised handlers."""

    handler_list: list[str] = params.handlers or []
    if not handler_list:
        well_known_url = params.url.replace("/rpc", "/well-known")
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(well_known_url)
                if resp.status_code == 200:
                    handler_list = resp.json().get("handlers", [])
        except Exception as exc:  # noqa: BLE001
            log.warning("/well-known fetch failed for %s: %s", params.workerId, exc)

    if not handler_list:
        raise RPCException(code=-32602, message="worker supports no handlers")

    await _upsert_worker(
        params.workerId,
        {
            "pool": params.pool,
            "url": params.url,
            "advertises": params.advertises,
            "handlers": handler_list,
        },
    )
    log.info(
        "worker %s registered (%s) handlers=%s",
        params.workerId,
        params.pool,
        handler_list,
    )
    return RegisterResult(ok=True).model_dump()


@dispatcher.method(WORKER_HEARTBEAT)
async def worker_heartbeat(params: HeartbeatParams) -> dict:
    known = await queue.exists(WORKER_KEY.format(params.workerId))
    if not known and not (params.pool and params.url):
        log.warning(
            "heartbeat from %s ignored: gateway lacks metadata; send pool+url or re-register",
            params.workerId,
        )
        return {"ok": False}

    mapping = {"last_seen": int(time.time())}
    if params.pool:
        mapping["pool"] = params.pool
    if params.url:
        mapping["url"] = params.url
    await queue.hset(WORKER_KEY.format(params.workerId), mapping=mapping)
    await queue.expire(WORKER_KEY.format(params.workerId), WORKER_TTL)
    return HeartbeatResult(ok=True).model_dump()


@dispatcher.method(WORKER_LIST)
async def worker_list(params: ListParams | None = None) -> list[dict]:
    """Return active workers, optionally filtered by *pool*."""

    pool = params.pool if params else None
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
        if "advertises" in w and isinstance(w["advertises"], str):
            try:
                w["advertises"] = json.loads(w["advertises"])
            except Exception:  # noqa: BLE001
                pass
        if "handlers" in w and isinstance(w["handlers"], str):
            try:
                w["handlers"] = json.loads(w["handlers"])
            except Exception:  # noqa: BLE001
                pass
        workers.append({"id": key.split(":", 1)[1], **{k: v for k, v in w.items()}})
    return ListResult([WorkerInfo.model_validate(w) for w in workers]).model_dump()


@dispatcher.method(WORK_FINISHED)
async def work_finished(taskId: str, status: str, result: dict | None = None) -> dict:
    t = await _load_task(taskId)
    if not t:
        log.warning("Work.finished for unknown task %s", taskId)
        return {"ok": False}

    t.status = Status(status)
    t.result = result
    now = time.time()
    started = getattr(t, "started_at", None)
    if status == "running" and started is None:
        t.started_at = now
    elif Status.is_terminal(status):
        if started is None:
            t.started_at = now
        t.finished_at = now

    await _save_task(t)
    await _persist(t)
    await _publish_task(t)
    if Status.is_terminal(status):
        await _finalize_parent_tasks(taskId)

    log.info("task %s completed: %s", taskId, status)
    return {"ok": True}
