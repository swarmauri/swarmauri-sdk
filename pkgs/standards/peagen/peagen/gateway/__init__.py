"""
dqueue.transport.gateway
────────────────────────
JSON-RPC gateway with verbose, structured logging.

Drop this file in place of the old gateway.py
and restart `scripts.dev_gateway`.
"""

from __future__ import annotations

import asyncio
import logging
from swarmauri_standard.loggers.Logger import Logger
import os
import uuid
import json
import httpx
import time
from json.decoder import JSONDecodeError
from typing import Optional

from fastapi import FastAPI, Request, Response
from peagen.plugins.queues import QueueBase

from peagen.transport import RPCDispatcher, RPCRequest, RPCError
from peagen.models import Task, Status, Base, TaskRun

from peagen.gateway.ws_server import router as ws_router

from peagen.gateway.db import engine
from peagen.plugins import PluginManager
from peagen._utils.config_loader import resolve_cfg
from peagen.gateway.db_helpers import ensure_status_enum
import peagen.defaults as defaults

from peagen.core.task_core import get_task_result

TASK_KEY = defaults.CONFIG["task_key"]

# ─────────────────────────── logging ────────────────────────────
LOG_LEVEL = os.getenv("DQ_LOG_LEVEL", "INFO").upper()
log = Logger(
    name="uvicorn",
    default_level=getattr(logging, LOG_LEVEL, logging.INFO),
)

# silence noisy deps but keep warnings
logging.getLogger("httpx").setLevel("WARNING")
logging.getLogger("uvicorn.error").setLevel("INFO")

# ─────────────────────────── FastAPI / state ────────────────────

app = FastAPI(title="Peagen Pool Manager Gateway")
app.include_router(ws_router)  # 1-liner, no prefix

cfg = resolve_cfg()
CONTROL_QUEUE = cfg.get("control_queue", defaults.CONFIG["control_queue"])
READY_QUEUE = cfg.get("ready_queue", defaults.CONFIG["ready_queue"])
PUBSUB_TOPIC = cfg.get("pubsub", defaults.CONFIG["pubsub"])
pm = PluginManager(cfg)

rpc = RPCDispatcher()
try:
    queue_plugin = pm.get("queues")
except KeyError:
    queue_plugin = None

queue: QueueBase = (
    queue_plugin.get_client() if hasattr(queue_plugin, "get_client") else queue_plugin
)
try:
    result_backend = pm.get("result_backends")
except KeyError:
    result_backend = None

# ─────────────────────────── Workers ────────────────────────────
# workers are stored as hashes:  queue.hset worker:<id> pool url advertises last_seen
WORKER_KEY = "worker:{}"  # format with workerId
WORKER_TTL = 15  # seconds before a worker is considered dead
TASK_TTL = 24 * 3600  # 24 h, adjust as needed


async def _upsert_worker(workerId: str, data: dict) -> None:
    """
    Persist worker metadata in Redis hash `worker:<id>`.
    • Any value that isn't bytes/str/int/float is json-encoded.
    • last_seen is stored as Unix epoch seconds.
    """
    coerced = {}
    for k, v in data.items():
        if isinstance(v, (bytes, str, int, float)):
            coerced[k] = v
        else:
            coerced[k] = json.dumps(v)  # serialize nested dicts, lists, etc.

    coerced["last_seen"] = int(time.time())  # heartbeat timestamp
    key = WORKER_KEY.format(workerId)  # e.g.  worker:7917b3bd
    await queue.hset(key, mapping=coerced)
    await queue.expire(key, WORKER_TTL)  # <<—— TTL refresh
    await _publish_event("worker.update", {"id": workerId, **data})


async def _publish_queue_length(pool: str) -> None:
    qlen = len(await queue.lrange(f"{READY_QUEUE}:{pool}", 0, -1))
    await _publish_event("queue.update", {"pool": pool, "length": qlen})


async def _live_workers_by_pool(pool: str) -> list[dict]:
    keys = await queue.keys("worker:*")
    workers = []
    now = int(asyncio.get_event_loop().time())
    for k in keys:
        w = await queue.hgetall(k)
        if not w:  # TTL expired or never registered
            continue
        if now - int(w["last_seen"]) > WORKER_TTL:
            continue  # stale
        if w["pool"] == pool:
            workers.append(w)
    return workers


# ───────── task helpers (hash + ttl) ────────────────────────────
def _task_key(tid: str) -> str:
    return TASK_KEY.format(tid)


async def _save_task(task: Task) -> None:
    """
    Upsert a task into its Redis hash and refresh TTL atomically.
    Stores the canonical JSON blob plus the status for quick look-up.
    """
    key = _task_key(task.id)
    blob = task.model_dump_json()

    await queue.hset(key, mapping={"blob": blob, "status": task.status.value})
    await queue.expire(key, TASK_TTL)


async def _load_task(tid: str) -> Task | None:
    data = await queue.hget(_task_key(tid), "blob")
    return Task.model_validate_json(data) if data else None


async def _select_tasks(selector: str) -> list[Task]:
    """Return tasks matching *selector*.

    A selector may be a task-id or ``label:<name>``.
    """
    if selector.startswith("label:"):
        label = selector.split(":", 1)[1]
        tasks = []
        for key in await queue.keys("task:*"):
            data = await queue.hget(key, "blob")
            if not data:
                continue
            t = Task.model_validate_json(data)
            if label in t.labels:
                tasks.append(t)
        return tasks
    t = await _load_task(selector)
    return [t] if t else []


# ──────────────────────   Results Backend ────────────────────────


async def _persist(task: Task) -> None:
    try:
        log.info(f"Writing {task}")
        await result_backend.store(TaskRun.from_task(task))
    except Exception as e:
        log.warning(f"_persist error '{e}'")


# ──────────────────────   Publish Event  ─────────────────────────


async def _publish_event(event_type: str, data: dict) -> None:
    """Send an event to WebSocket subscribers."""

    event = {
        "type": event_type,
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "data": data,
    }
    await queue.publish(PUBSUB_TOPIC, json.dumps(event))


async def _publish_task(task: Task) -> None:
    await _publish_event("task.update", task.model_dump())


# ─────────────────────────── RPC endpoint ───────────────────────
@app.post("/rpc", summary="JSON-RPC 2.0 endpoint")
async def rpc_endpoint(request: Request):
    try:
        raw = await request.json()
    except JSONDecodeError:
        log.warning("parse error from %s", request.client.host)
        return Response(
            content='{"jsonrpc":"2.0","error":{"code":-32700,"message":"Parse error"},"id":null}',
            status_code=400,
            media_type="application/json",
        )

    def _ensure_id(obj: dict) -> dict:
        if obj.get("id") is None:
            obj["id"] = str(uuid.uuid4())
        return RPCRequest.model_validate(obj).model_dump()

    if isinstance(raw, list):
        payload = [_ensure_id(item) for item in raw]
    else:
        payload = _ensure_id(raw)

    log.debug("RPC in  <- %s", payload)
    resp = await rpc.dispatch(payload)
    if isinstance(resp, dict) and "error" in resp:
        method = payload.get("method") if isinstance(payload, dict) else "batch"
        log.warning(f"{method} '{resp['error']}'")
    log.debug("RPC out -> %s", resp)
    return resp


# ─────────────────────────── Pool RPCs ──────────────────────────
@rpc.method("Pool.create")
async def pool_create(name: str):
    await queue.sadd("pools", name)
    log.info("pool created: %s", name)
    return {"name": name}


@rpc.method("Pool.join")
async def pool_join(name: str):
    member = str(uuid.uuid4())[:8]
    await queue.sadd(f"pool:{name}:members", member)
    log.info("member %s joined pool %s", member, name)
    return {"memberId": member}


# ─────────────────────────── Task RPCs ──────────────────────────
@rpc.method("Task.submit")
async def task_submit(
    pool: str,
    payload: dict,
    taskId: Optional[str],
    deps: list[str] | None = None,
    edge_pred: str | None = None,
    labels: list[str] | None = None,
    in_degree: int | None = None,
    config_toml: str | None = None,
):
    await queue.sadd("pools", pool)  # track pool even if not created

    if taskId and await _load_task(taskId):
        new_id = str(uuid.uuid4())
        log.warning("task id collision: %s → %s", taskId, new_id)
        taskId = new_id

    task = Task(
        id=taskId or str(uuid.uuid4()),
        pool=pool,
        payload=payload,
        deps=deps or [],
        edge_pred=edge_pred,
        labels=labels or [],
        in_degree=in_degree or 0,
        config_toml=config_toml,
    )

    # 1) put on the queue for the scheduler
    await queue.rpush(f"{READY_QUEUE}:{pool}", task.model_dump_json())
    await _publish_queue_length(pool)

    # 2) save hash + TTL
    await _save_task(task)

    # 3) persist to Postgres & emit CloudEvent (helpers you already have)
    await _persist(task)
    await _publish_task(task)

    log.info("task %s queued in %s (ttl=%ss)", task.id, pool, TASK_TTL)
    return {"taskId": task.id}


@rpc.method("Task.cancel")
async def task_cancel(selector: str):
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply(
        "cancel", queue, targets, READY_QUEUE, TASK_TTL
    )
    log.info("cancel %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Task.pause")
async def task_pause(selector: str):
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply(
        "pause", queue, targets, READY_QUEUE, TASK_TTL
    )
    log.info("pause %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Task.resume")
async def task_resume(selector: str):
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply(
        "resume", queue, targets, READY_QUEUE, TASK_TTL
    )
    log.info("resume %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Task.retry")
async def task_retry(selector: str):
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply(
        "retry", queue, targets, READY_QUEUE, TASK_TTL
    )
    log.info("retry %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Task.retry_from")
async def task_retry_from(selector: str):
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply(
        "retry_from", queue, targets, READY_QUEUE, TASK_TTL
    )
    log.info("retry_from %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Guard.set")
async def guard_set(label: str, spec: dict):
    await queue.hset(f"guard:{label}", mapping=spec)
    log.info("guard set %s", label)
    return {"ok": True}


@rpc.method("Task.patch")
async def task_patch(taskId: str, changes: dict) -> dict:
    """Update persisted metadata for an existing task."""
    task = await _load_task(taskId)
    if not task:
        raise ValueError("task not found")

    for field, value in changes.items():
        if field not in Task.model_fields:
            continue
        if field == "status":
            value = Status(value)
        setattr(task, field, value)

    await _save_task(task)
    await _persist(task)
    await _publish_task(task)
    log.info("task %s patched with %s", taskId, ",".join(changes.keys()))
    return task.model_dump()


@rpc.method("Task.get")
async def task_get(taskId: str):
    # hot cache
    if t := await _load_task(taskId):
        return t.model_dump()

    # authoritative fallback (Postgres)
    try:
        return await get_task_result(taskId)  # raises ValueError if not found
    except ValueError as exc:
        # surface a proper JSON-RPC error so the envelope is valid
        raise RPCError(code=-32001, message=str(exc))


@rpc.method("Pool.listTasks")
async def pool_list(poolName: str):
    ids = await queue.lrange(f"{READY_QUEUE}:{poolName}", 0, -1)
    return [Task.model_validate_json(r).model_dump() for r in ids]


# ─────────────────────────── Worker RPCs ────────────────────────
@rpc.method("Worker.register")
async def worker_register(workerId: str, pool: str, url: str, advertises: dict):
    await _upsert_worker(workerId, {"pool": pool, "url": url, "advertises": advertises})
    log.info("worker %s registered (%s)", workerId, pool)
    return {"ok": True}


@rpc.method("Worker.heartbeat")
async def worker_heartbeat(
    workerId: str, metrics: dict, pool: str | None = None, url: str | None = None
):
    # If gateway has no record (after crash), pool & url are expected
    known = await queue.exists(WORKER_KEY.format(workerId))
    if not known and not (pool and url):
        log.warning(
            "heartbeat from %s ignored: gateway lacks metadata; send pool+url or re-register",
            workerId,
        )
        return {"ok": False}

    await _upsert_worker(workerId, {"pool": pool, "url": url})
    return {"ok": True}


@rpc.method("Work.finished")
async def work_finished(taskId: str, status: str, result: dict | None = None):
    t = await _load_task(taskId)
    if not t:
        log.warning("Work.finished for unknown task %s", taskId)
        return {"ok": False}

    # update in-memory object
    t.status = Status(status)
    t.result = result

    # persist everywhere
    await _save_task(t)
    await _persist(t)
    await _publish_task(t)

    log.info("task %s completed: %s", taskId, status)
    return {"ok": True}


# ─────────────────────────── Scheduler loop ─────────────────────
async def scheduler():
    log.info("scheduler started")
    async with httpx.AsyncClient(timeout=10, http2=True) as client:
        while True:
            # iterate over pools with queued work
            pools = await queue.smembers("pools")
            if not pools:
                await asyncio.sleep(0.25)
                continue

            # build key list once per tick → ["queue:demo", "queue:beta", ...]
            keys = [f"{READY_QUEUE}:{p}" for p in pools]

            # BLPOP across *all* pools, 0.5-sec timeout
            res = await queue.blpop(keys, 0.5)
            if res is None:
                # no work ready this half-second
                continue

            queue_key, task_raw = res  # guaranteed 2-tuple here
            pool = queue_key.split(":", 1)[1]  # remove prefix '<READY_QUEUE>:'
            await _publish_queue_length(pool)
            task = Task.model_validate_json(task_raw)

            # pick first live worker for that pool
            worker_list = await _live_workers_by_pool(pool)
            if not worker_list:
                log.info("no active worker for %s, re-queue %s", pool, task.id)
                await queue.rpush(queue_key, task_raw)  # push back
                await _publish_queue_length(pool)
                await asyncio.sleep(5)
                continue

            target = worker_list[0]
            rpc_req = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "Work.start",
                "params": {"task": task.model_dump()},
            }

            try:
                resp = await client.post(target["url"], json=rpc_req)
                if resp.status_code != 200:
                    raise RuntimeError(f"HTTP {resp.status_code}")

                task.status = Status.dispatched
                await _save_task(task)
                await _persist(task)
                await _publish_task(task)
                log.info(
                    "dispatch %s → %s (HTTP %d)",
                    task.id,
                    target["url"],
                    resp.status_code,
                )

            except Exception as exc:
                log.warning("dispatch failed (%s) for %s; re-queueing", exc, task.id)
                await queue.rpush(queue_key, task_raw)  # retry later
                await _publish_queue_length(pool)


# ─────────────────────────────── Healthcheck ───────────────────────────────
@app.get("/health", tags=["health"])
async def health() -> dict:
    """
    Simple readiness probe. Returns 200 OK as long as the app is running.
    Docker’s healthcheck will curl this endpoint.
    """
    return {"status": "ok"}

\
# ───────────────────────────────    Startup  ───────────────────────────────
@app.on_event("startup")
async def _on_start():
    if engine.url.get_backend_name() != "sqlite":
        await ensure_status_enum(engine)
    else:
        async with engine.begin() as conn:
            # run once – creates task_runs if it doesn't exist
            await conn.run_sync(Base.metadata.create_all)
    asyncio.create_task(scheduler())
