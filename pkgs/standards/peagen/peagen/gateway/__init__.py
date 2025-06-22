"""
peagen.gateway
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

import pgpy
from fastapi import Body, FastAPI, Request, Response, HTTPException
from peagen.plugins.queues import QueueBase

from peagen.transport import RPCDispatcher, RPCRequest, RPCException
from peagen.models import Task, Status, Base, TaskRun

from peagen.gateway.ws_server import router as ws_router

from importlib import reload
from peagen.gateway import db as _db
from peagen.plugins import PluginManager
from peagen._utils.config_loader import resolve_cfg
from peagen.gateway.db_helpers import (
    ensure_status_enum,
    upsert_secret,
    fetch_secret,
    delete_secret,
    record_unknown_handler,
    fetch_banned_ips,
    mark_ip_banned,
)
import peagen.defaults as defaults
from peagen.core import migrate_core
from peagen.core.task_core import get_task_result

_db = reload(_db)
engine = _db.engine
Session = _db.Session

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
READY = False

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

# ─────────────────────────── Key/Secret store ───────────────────
TRUSTED_USERS: dict[str, str] = {}

# ─────────────────────────── Workers ────────────────────────────
# workers are stored as hashes:  queue.hset worker:<id> pool url advertises last_seen
WORKER_KEY = "worker:{}"  # format with workerId
WORKER_TTL = 15  # seconds before a worker is considered dead
TASK_TTL = 24 * 3600  # 24 h, adjust as needed

# ─────────────────────────── IP tracking ─────────────────────────
BAN_THRESHOLD = 10
KNOWN_IPS: set[str] = set()
BANNED_IPS: set[str] = set()


def _supports(method: str | None) -> bool:
    """Return ``True`` if *method* is registered."""

    return method in rpc._methods


async def _reject(ip: str, req_id: str | None, method: str | None) -> dict:
    """Return an error response and track abuse."""

    async with Session() as session:
        count = await record_unknown_handler(session, ip)
    if count >= BAN_THRESHOLD:
        BANNED_IPS.add(ip)
        async with Session() as session:
            await mark_ip_banned(session, ip)
        log.warning("banned ip %s", ip)
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": "Method not found",
            "data": {"method": str(method)},
        },
        "id": req_id,
    }


async def _prevalidate(payload: dict | list, ip: str) -> dict | None:
    """Validate incoming JSON-RPC payload."""

    if isinstance(payload, list):
        for item in payload:
            if not _supports(item.get("method")):
                return await _reject(ip, item.get("id"), item.get("method"))
        return None

    if not _supports(payload.get("method")):
        return await _reject(ip, payload.get("id"), payload.get("method"))
    return None


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
    # ensure the worker's pool is tracked so WebSocket clients
    # receive queue length updates even before a task is submitted
    pool = data.get("pool")
    if pool:
        await queue.sadd("pools", pool)
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


async def _flush_state() -> None:
    """Persist all tasks from Redis to Postgres and close the queue client."""
    if not queue:
        return
    keys = await queue.keys("task:*")
    for key in keys:
        data = await queue.hget(key, "blob")
        if not data:
            continue
        task = Task.model_validate_json(data)
        if result_backend:
            await result_backend.store(TaskRun.from_task(task))
    if hasattr(queue, "client"):
        await queue.client.aclose()


async def _publish_task(task: Task) -> None:
    data = task.model_dump()
    if task.duration is not None:
        data["duration"] = task.duration
    await _publish_event("task.update", data)


async def _finalize_parent_tasks(child_id: str) -> None:
    """Mark parent tasks as completed once all children finish."""
    keys = await queue.keys("task:*")
    for key in keys:
        data = await queue.hget(key, "blob")
        if not data:
            continue
        parent = Task.model_validate_json(data)
        children = []
        if parent.result and isinstance(parent.result, dict):
            children = parent.result.get("children") or []
        if child_id not in children:
            continue
        all_done = True
        for cid in children:
            ct = await _load_task(cid)
            if not ct or not Status.is_terminal(ct.status):
                all_done = False
                break
        if all_done and parent.status != Status.success:
            parent.status = Status.success
            parent.finished_at = time.time()
            await _save_task(parent)
            await _persist(parent)
            await _publish_task(parent)


async def _backlog_scanner(interval: float = 5.0) -> None:
    """Periodically run `_finalize_parent_tasks` to clear any backlog."""
    log.info("backlog scanner started")
    while True:
        keys = await queue.keys("task:*")
        for key in keys:
            data = await queue.hget(key, "blob")
            if not data:
                continue
            t = Task.model_validate_json(data)
            children = []
            if t.result and isinstance(t.result, dict):
                children = t.result.get("children") or []
            for cid in children:
                await _finalize_parent_tasks(cid)
        await asyncio.sleep(interval)


# ─────────────────────────── RPC endpoint ───────────────────────
@app.post("/rpc", summary="JSON-RPC 2.0 endpoint")
async def rpc_endpoint(request: Request):
    ip = request.client.host
    KNOWN_IPS.add(ip)
    if ip in BANNED_IPS:
        log.warning("blocked request from banned ip %s", ip)
        return Response(
            content='{"jsonrpc":"2.0","error":{"code":-32098,"message":"Banned"},"id":null}',
            status_code=403,
            media_type="application/json",
        )
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
    pre = await _prevalidate(payload, ip)
    if pre is not None:
        return pre
    resp = await rpc.dispatch(payload)

    async def _check_unknown(r: dict, method: str) -> None:
        if r.get("error", {}).get("code") == -32601:
            r["error"]["data"] = {"method": method}
            async with Session() as session:
                count = await record_unknown_handler(session, ip)
            if count >= BAN_THRESHOLD:
                BANNED_IPS.add(ip)
                async with Session() as session:
                    await mark_ip_banned(session, ip)
                log.warning("banned ip %s", ip)

    if isinstance(resp, dict) and "error" in resp:
        method = payload.get("method") if isinstance(payload, dict) else "batch"
        log.warning(f"{method} '{resp['error']}'")
        await _check_unknown(resp, method)
    elif isinstance(resp, list):
        for r in resp:
            if isinstance(r, dict) and "error" in r:
                await _check_unknown(r, "batch")
    log.debug("RPC out -> %s", resp)
    return resp


# ─────────────────────────── Key/Secret RPC ─────────────────────


@rpc.method("Keys.upload")
async def keys_upload(public_key: str) -> dict:
    """Store a trusted public key."""
    key = pgpy.PGPKey()
    key.parse(public_key)
    TRUSTED_USERS[key.fingerprint] = public_key
    log.info("key uploaded: %s", key.fingerprint)
    return {"fingerprint": key.fingerprint}


@rpc.method("Keys.fetch")
async def keys_fetch() -> dict:
    """Return all trusted keys indexed by fingerprint."""
    return TRUSTED_USERS


@rpc.method("Keys.delete")
async def keys_delete(fingerprint: str) -> dict:
    """Remove a public key by its fingerprint."""
    TRUSTED_USERS.pop(fingerprint, None)
    log.info("key removed: %s", fingerprint)
    return {"ok": True}


@rpc.method("Secrets.add")
async def secrets_add(
    name: str,
    secret: str,
    tenant_id: str = "default",
    owner_fpr: str = "unknown",
    version: int | None = None,
) -> dict:
    """Store an encrypted secret."""
    async with Session() as session:
        await upsert_secret(session, tenant_id, owner_fpr, name, secret)
        await session.commit()
    log.info("secret stored: %s", name)
    return {"ok": True}


@rpc.method("Secrets.get")
async def secrets_get(name: str, tenant_id: str = "default") -> dict:
    """Retrieve an encrypted secret."""
    async with Session() as session:
        row = await fetch_secret(session, tenant_id, name)
    if not row:
        raise RPCException(code=-32000, message="secret not found")
    return {"secret": row.cipher}


@rpc.method("Secrets.delete")
async def secrets_delete(
    name: str, tenant_id: str = "default", version: int | None = None
) -> dict:
    """Remove a secret by name."""
    async with Session() as session:
        await delete_secret(session, tenant_id, name)
        await session.commit()
    log.info("secret removed: %s", name)

    return {"ok": True}


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

    action = (payload or {}).get("action")
    handlers: set[str] = set()
    for w in await _live_workers_by_pool(pool):
        raw = w.get("handlers", [])
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:  # noqa: BLE001
                raw = []
        handlers.update(raw)
    if action is None or action not in handlers:
        raise RPCException(
            code=-32601, message="Method not found", data={"method": str(action)}
        )

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

    count = await control_handler.apply("cancel", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("cancel %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Task.pause")
async def task_pause(selector: str):
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("pause", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("pause %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Task.resume")
async def task_resume(selector: str):
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("resume", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("resume %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Task.retry")
async def task_retry(selector: str):
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("retry", queue, targets, READY_QUEUE, TASK_TTL)
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
    if "result" in changes and isinstance(changes["result"], dict):
        children = changes["result"].get("children")
        if children:
            for cid in children:
                await _finalize_parent_tasks(cid)
    log.info("task %s patched with %s", taskId, ",".join(changes.keys()))
    return task.model_dump()


@rpc.method("Task.get")
async def task_get(taskId: str):
    # hot cache
    if t := await _load_task(taskId):
        data = t.model_dump()
        if t.duration is not None:
            data["duration"] = t.duration
        return data

    # authoritative fallback (Postgres)
    try:
        return await get_task_result(taskId)  # raises ValueError if not found
    except ValueError as exc:
        # surface a proper JSON-RPC error so the envelope is valid
        raise RPCException(code=-32001, message=str(exc))


@rpc.method("Pool.listTasks")
async def pool_list(poolName: str):
    ids = await queue.lrange(f"{READY_QUEUE}:{poolName}", 0, -1)
    tasks = []
    for r in ids:
        t = Task.model_validate_json(r)
        data = t.model_dump()
        if t.duration is not None:
            data["duration"] = t.duration
        tasks.append(data)
    return tasks


# ─────────────────────────── Worker RPCs ────────────────────────
@rpc.method("Worker.register")
async def worker_register(workerId: str, pool: str, url: str, advertises: dict):
    handlers: list[str] = []
    well_known_url = url.replace("/rpc", "/well-known")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(well_known_url)
            if resp.status_code == 200:
                handlers = resp.json().get("handlers", [])
    except Exception as exc:  # noqa: BLE001
        log.warning("/well-known fetch failed for %s: %s", workerId, exc)

    await _upsert_worker(
        workerId,
        {"pool": pool, "url": url, "advertises": advertises, "handlers": handlers},
    )
    log.info("worker %s registered (%s) handlers=%s", workerId, pool, handlers)
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


@rpc.method("Worker.list")
async def worker_list(pool: str | None = None) -> list[dict]:
    """Return active workers, optionally filtered by *pool*."""

    keys = await queue.keys("worker:*")
    workers = []
    now = int(asyncio.get_event_loop().time())
    for key in keys:
        w = await queue.hgetall(key)
        if not w:
            continue
        if now - int(w.get("last_seen", 0)) > WORKER_TTL:
            continue
        if pool and w.get("pool") != pool:
            continue
        workers.append(
            {
                "id": key.split(":", 1)[1],
                **{k: v for k, v in w.items()},
            }
        )
    return workers


@rpc.method("Work.finished")
async def work_finished(taskId: str, status: str, result: dict | None = None):
    t = await _load_task(taskId)
    if not t:
        log.warning("Work.finished for unknown task %s", taskId)
        return {"ok": False}

    # update in-memory object
    t.status = Status(status)
    t.result = result
    now = time.time()
    if status == "running" and t.started_at is None:
        t.started_at = now
    elif Status.is_terminal(status):
        if t.started_at is None:
            t.started_at = now
        t.finished_at = now

    # persist everywhere
    await _save_task(t)
    await _persist(t)
    await _publish_task(t)
    if Status.is_terminal(status):
        await _finalize_parent_tasks(taskId)

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


# ────────────────────────── Key Management ──────────────────────────
@app.post("/keys", tags=["keys"])
async def upload_key(public_key: str = Body(..., embed=True)) -> dict:
    key = pgpy.PGPKey()
    key.parse(public_key)
    TRUSTED_USERS[key.fingerprint] = public_key
    return {"fingerprint": key.fingerprint}


@app.get("/keys", tags=["keys"])
async def list_keys() -> dict:
    return {"keys": list(TRUSTED_USERS.keys())}


@app.delete("/keys/{fingerprint}", tags=["keys"])
async def delete_key(fingerprint: str) -> dict:
    TRUSTED_USERS.pop(fingerprint, None)
    return {"removed": fingerprint}


# ────────────────────────── Secret Endpoints ─────────────────────────
@app.post("/secrets", tags=["secrets"])
async def add_secret(
    name: str = Body(...),
    secret: str = Body(...),
    tenant_id: str = "default",
    owner_fpr: str = "unknown",
) -> dict:
    async with Session() as session:
        await upsert_secret(session, tenant_id, owner_fpr, name, secret)
        await session.commit()
    return {"stored": name}


@app.get("/secrets/{name}", tags=["secrets"])
async def get_secret(name: str, tenant_id: str = "default") -> dict:
    async with Session() as session:
        row = await fetch_secret(session, tenant_id, name)
    if not row:
        return {"error": "not found"}
    return {"secret": row.cipher}


@app.delete("/secrets/{name}", tags=["secrets"])
async def delete_secret_route(name: str, tenant_id: str = "default") -> dict:
    async with Session() as session:
        await delete_secret(session, tenant_id, name)
        await session.commit()
    return {"removed": name}


# ─────────────────────────────── Healthcheck ───────────────────────────────
@app.get("/healthz", tags=["health"])
async def health() -> dict:
    """
    Simple readiness probe. Returns 200 OK once startup tasks complete.
    Docker’s healthcheck will curl this endpoint.
    """
    if READY:
        return {"status": "ok"}
    raise HTTPException(status_code=503, detail="starting")


# ───────────────────────────────    Startup  ───────────────────────────────
@app.on_event("startup")
async def _on_start():
    log.info("gateway startup initiated")
    result = migrate_core.alembic_upgrade()
    if not result.get("ok", False):
        log.error("migration failed: %s", result.get("error"))
        raise RuntimeError(result.get("error"))
    log.info("migrations applied; verifying database schema")
    if engine.url.get_backend_name() != "sqlite":
        # ensure schema is up to date for Postgres deployments
        await ensure_status_enum(engine)
    else:
        async with engine.begin() as conn:
            # run once – creates task_runs if it doesn't exist
            await conn.run_sync(Base.metadata.create_all)
        log.info("SQLite metadata initialized")

    async with Session() as session:
        banned = await fetch_banned_ips(session)
    BANNED_IPS.update(banned)

    log.info("database migrations complete")
    asyncio.create_task(scheduler())
    asyncio.create_task(_backlog_scanner())
    log.info("scheduler and backlog scanner started")
    global READY
    READY = True
    log.info("gateway startup complete")


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    log.info("gateway shutdown initiated")
    await _flush_state()
    log.info("state flushed to persistent storage")
    await engine.dispose()
    log.info("database connections closed")
