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


import pgpy
from fastapi import FastAPI, Request, Response, HTTPException
from peagen.plugins.queues import QueueBase

from peagen.transport import RPCDispatcher, RPCRequest
from peagen.transport.jsonrpc import RPCException
from peagen.orm import Base, Status, Task
from peagen.schemas import TaskRead, TaskCreate, TaskUpdate
from peagen.orm.task.task import TaskModel
from peagen.orm.task.task_run import TaskRun

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
from peagen.errors import (
    DispatchHTTPError,
    MissingActionError,
    MigrationFailureError,
    NoWorkerAvailableError,
    TaskNotFoundError,
)
import peagen.defaults as defaults
from peagen.defaults import BAN_THRESHOLD
from peagen.defaults.error_codes import ErrorCode
from peagen.core import migrate_core
from peagen.core.task_core import get_task_result

_db = reload(_db)
engine = _db.engine
Session = _db.Session

TASK_KEY = defaults.CONFIG["task_key"]

# ─────────────────────────── logging ────────────────────────────
LOG_LEVEL = os.getenv("DQ_LOG_LEVEL", "INFO").upper()
log = Logger(
    name="gw",
    default_level=getattr(logging, LOG_LEVEL, logging.INFO),
)

# dedicated logger for the scheduler loop
sched_log = Logger(
    name="scheduler",
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

KNOWN_IPS: set[str] = set()
BANNED_IPS: set[str] = set()


def _supports(method: str | None) -> bool:
    """Return ``True`` if *method* is registered."""

    return method in rpc._methods


async def _reject(
    ip: str,
    req_id: str | None,
    method: str | None,
    *,
    code: int = -32601,
    message: str = "Method not found",
) -> dict:
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
            "code": code,
            "message": message,
            "data": {"method": str(method)},
        },
        "id": req_id,
    }


async def _prevalidate(payload: dict | list, ip: str) -> dict | None:
    """Validate incoming JSON-RPC payload."""

    if isinstance(payload, list):
        for item in payload:
            if item.get("jsonrpc") and item.get("jsonrpc") != "2.0":
                return await _reject(
                    ip,
                    item.get("id"),
                    item.get("method"),
                    code=-32600,
                    message="Invalid Request",
                )
            if item.get("method") is None or not _supports(item.get("method")):
                return await _reject(ip, item.get("id"), item.get("method"))
        return None

    if payload.get("jsonrpc") and payload.get("jsonrpc") != "2.0":
        return await _reject(
            ip,
            payload.get("id"),
            payload.get("method"),
            code=-32600,
            message="Invalid Request",
        )
    if payload.get("method") is None or not _supports(payload.get("method")):
        return await _reject(ip, payload.get("id"), payload.get("method"))
    return None


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


# ───────── task helpers (hash + ttl) ────────────────────────────


def to_orm(data: TaskCreate | TaskUpdate) -> TaskModel:
    """Convert a :class:`TaskCreate` or :class:`TaskUpdate` to a ``TaskModel``."""

    return TaskModel(**data.model_dump())


def to_schema(row: TaskModel) -> TaskRead:
    """Convert a ``TaskModel`` row to its ``TaskRead`` schema."""

    return TaskRead.from_orm(row)


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


async def _load_task(tid: str) -> TaskRead | None:
    data = await queue.hget(_task_key(tid), "blob")
    return TaskRead.model_validate_json(data) if data else None


async def _select_tasks(selector: str) -> list[TaskRead]:
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
            t = TaskRead.model_validate_json(data)
            if label in t.labels:
                tasks.append(t)
        return tasks
    t = await _load_task(selector)
    return [t] if t else []


# ──────────────────────   Results Backend ────────────────────────


async def _persist(task: TaskModel | TaskCreate | TaskUpdate) -> None:
    """Persist a task to the results backend."""

    try:
        log.info("persisting task %s", task.id)
        orm_task = task if isinstance(task, TaskModel) else to_orm(task)
        await result_backend.store(TaskRun.from_task(orm_task))
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
        task = TaskRead.model_validate_json(data)
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
        parent = TaskRead.model_validate_json(data)
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
            t = TaskRead.model_validate_json(data)
            children = []
            if t.result and isinstance(t.result, dict):
                children = t.result.get("children") or []
            for cid in children:
                await _finalize_parent_tasks(cid)
        await asyncio.sleep(interval)


# ────────────────────── client IP extraction ─────────────────────


def _get_client_ip(request: Request) -> str:
    """Return the client's real IP address.

    The function checks standard forwarding headers first and falls back to
    ``request.client.host`` when none are present.

    Args:
        request: Incoming FastAPI request.

    Returns:
        str: The detected client IP address.
    """

    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    return real_ip if real_ip else request.client.host


# ─────────────────────────── RPC endpoint ───────────────────────
@app.post("/rpc", summary="JSON-RPC 2.0 endpoint")
async def rpc_endpoint(request: Request):
    ip = _get_client_ip(request)
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
        code = r.get("error", {}).get("code")
        if code in (-32601, -32600):
            if code == -32601:
                r["error"]["data"] = {"method": method}
            async with Session() as session:
                count = await record_unknown_handler(session, ip)
            if count >= BAN_THRESHOLD:
                BANNED_IPS.add(ip)
                async with Session() as session:
                    await mark_ip_banned(session, ip)
                log.warning("banned ip %s", ip)

    status = 200

    def _not_found(r: dict) -> bool:
        return r.get("error", {}).get("code") == ErrorCode.SECRET_NOT_FOUND

    if isinstance(resp, dict) and "error" in resp:
        method = payload.get("method") if isinstance(payload, dict) else "batch"
        log.warning(f"{method} '{resp['error']}'")
        await _check_unknown(resp, method)
        if _not_found(resp):
            status = 404
    elif isinstance(resp, list):
        for r in resp:
            if isinstance(r, dict) and "error" in r:
                await _check_unknown(r, "batch")
                if _not_found(r):
                    status = 404
    log.debug("RPC out -> %s", resp)
    return Response(
        content=json.dumps(resp), status_code=status, media_type="application/json"
    )


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
        raise RPCException(
            code=ErrorCode.SECRET_NOT_FOUND,
            message="secret not found",
        )
    return {"secret": row.cipher}


@rpc.method("Secrets.delete")
async def secrets_delete(
    name: str,
    tenant_id: str = "default",
    version: int | None = None,
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
    taskId: str | None = None,
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
    if action is not None and action not in handlers:
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
        raise TaskNotFoundError(taskId)

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
    try:
        uuid.UUID(taskId)
    except ValueError:
        raise RPCException(code=-32602, message="Invalid task id")
    # hot cache
    if t := await _load_task(taskId):
        data = t.model_dump()
        if t.duration is not None:
            data["duration"] = t.duration
        return data

    # authoritative fallback (Postgres)
    try:
        return await get_task_result(taskId)  # raises TaskNotFoundError if missing
    except TaskNotFoundError as exc:
        # surface a proper JSON-RPC error so the envelope is valid
        raise RPCException(code=ErrorCode.TASK_NOT_FOUND, message=str(exc))


@rpc.method("Pool.listTasks")
async def pool_list(poolName: str, limit: int | None = None, offset: int = 0):
    """Return tasks queued for *poolName* with optional pagination."""

    start = max(offset, 0)
    end = -1 if limit is None else start + limit - 1
    ids = await queue.lrange(f"{READY_QUEUE}:{poolName}", start, end)
    tasks = []
    for r in ids:
        t = TaskRead.model_validate_json(r)
        data = t.model_dump()
        if t.duration is not None:
            data["duration"] = t.duration
        tasks.append(data)
    return tasks


# ─────────────────────────── Worker RPCs ────────────────────────
@rpc.method("Worker.register")
async def worker_register(
    workerId: str,
    pool: str,
    url: str,
    advertises: dict,
    handlers: list[str] | None = None,
):
    """Register a worker and persist its advertised handlers."""

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
    now = int(time.time())
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


# ────────────────────────── Helpers ──────────────────────────
async def _fail_task(task: Task, error: Exception) -> None:
    """Mark *task* as failed and persist the error message."""
    task.status = Status.failed
    task.result = {"error": str(error)}
    task.finished_at = time.time()
    await _save_task(task)
    await _persist(task)
    await _publish_task(task)


# ─────────────────────────── Scheduler loop ─────────────────────
async def scheduler():
    sched_log.info("scheduler started")
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
            task = TaskRead.model_validate_json(task_raw)

            # pick a worker that supports the task's action
            worker_list = await _live_workers_by_pool(pool)
            action = task.payload.get("action")
            if not action:
                sched_log.warning("task %s missing action; marking failed", task.id)
                await _fail_task(task, MissingActionError())
                continue

            target = _pick_worker(worker_list, action)
            if not target:
                sched_log.warning(
                    "no worker for %s:%s, failing %s",
                    pool,
                    action,
                    task.id,
                )
                await _fail_task(task, NoWorkerAvailableError(pool, action))
                continue
            rpc_req = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "Work.start",
                "params": {"task": task.model_dump()},
            }

            try:
                resp = await client.post(target["url"], json=rpc_req)
                if resp.status_code != 200:
                    raise DispatchHTTPError(resp.status_code)

                task.status = Status.dispatched
                await _save_task(task)
                await _persist(task)
                await _publish_task(task)
                sched_log.info(
                    "dispatch %s → %s (HTTP %d)",
                    task.id,
                    target["url"],
                    resp.status_code,
                )

            except Exception as exc:
                sched_log.warning(
                    "dispatch failed (%s) for %s; re-queueing", exc, task.id
                )
                if "id" in target:
                    await _remove_worker(target["id"])
                await queue.rpush(queue_key, task_raw)  # retry later
                await _publish_queue_length(pool)


# ────────────────────────── Key Management ──────────────────────────
async def upload_key(public_key: str) -> dict:
    key = pgpy.PGPKey()
    key.parse(public_key)
    TRUSTED_USERS[key.fingerprint] = public_key
    return {"fingerprint": key.fingerprint}


async def list_keys() -> dict:
    return {"keys": list(TRUSTED_USERS.keys())}


async def delete_key(fingerprint: str) -> dict:
    TRUSTED_USERS.pop(fingerprint, None)
    return {"removed": fingerprint}


# ────────────────────────── Secret Endpoints ─────────────────────────
async def add_secret(
    name: str,
    secret: str,
    tenant_id: str = "default",
    owner_fpr: str = "unknown",
) -> dict:
    async with Session() as session:
        await upsert_secret(session, tenant_id, owner_fpr, name, secret)
        await session.commit()
    return {"stored": name}


async def get_secret(name: str, tenant_id: str = "default") -> dict:
    async with Session() as session:
        row = await fetch_secret(session, tenant_id, name)
    if not row:
        return {"error": "not found"}
    return {"secret": row.cipher}


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
        error_msg = result.get("error")
        log.error("migration failed: %s", error_msg)
        raise MigrationFailureError(str(error_msg))
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
