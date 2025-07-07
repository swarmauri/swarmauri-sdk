"""
peagen.gateway
────────────────────────
JSON-RPC gateway with verbose, structured logging.

Drop this file in place of the old gateway.py
and restart `scripts.dev_gateway`.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from importlib import reload
from json.decoder import JSONDecodeError
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException, Request, Response

import peagen.defaults as defaults
from peagen._utils.config_loader import resolve_cfg
from peagen.core import migrate_core
from peagen.defaults import BAN_THRESHOLD
from peagen.errors import (
    DispatchHTTPError,
    MigrationFailureError,
    MissingActionError,
    NoWorkerAvailableError,
)
from peagen.gateway import db as _db
from peagen.gateway import db_helpers
from peagen.gateway.rpc import api_router
from peagen.gateway.db_helpers import mark_ip_banned, record_unknown_handler
from peagen.gateway.ws_server import router as ws_router
from peagen.orm import Base, TaskModel, TaskRunModel
from peagen.plugins import PluginManager
from peagen.plugins.queues import QueueBase
from peagen.transport import (
    Request as RPCEnvelope,
)
from peagen.transport import (
    Request as RPCRequest,
)
from peagen.transport import (
    RPCDispatcher,
    _registry,
    parse_request,
)
from peagen.transport.error_codes import ErrorCode
from peagen.transport.jsonrpc import RPCException as RPCException
from peagen.transport.jsonrpc_schemas import Status
from peagen.transport.jsonrpc_schemas.work import WORK_START
from swarmauri_standard.loggers.Logger import Logger

_db = reload(_db)
engine = _db.engine
Session = _db.Session

# Columns available on the TaskModel ORM table. Used to filter
# incoming task dictionaries before persistence.
_ORM_COLUMNS = {c.name for c in TaskModel.__table__.columns}

TASK_KEY = defaults.CONFIG["task_key"]
TaskBlob = Dict[str, Any]  # id / pool / payload / … as plain JSON

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
app.include_router(ws_router)
app.include_router(api_router)
READY = False

cfg = resolve_cfg()
CONTROL_QUEUE = cfg.get("control_queue", defaults.CONFIG["control_queue"])
READY_QUEUE = cfg.get("ready_queue", defaults.CONFIG["ready_queue"])
PUBSUB_TOPIC = cfg.get("pubsub", defaults.CONFIG["pubsub"])
pm = PluginManager(cfg)

dispatcher = RPCDispatcher()
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


# ───────────────────────── Work Capabiility ──────────────────────
def _supports(method: str | None) -> bool:
    """Return ``True`` if *method* is registered."""
    return method in dispatcher._methods


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


def _task_key(tid: str) -> str:
    return TASK_KEY.format(tid)


# ------------------------------------------------------------------
# Helpers that operate purely on raw JSON blobs (TaskBlob)
# ------------------------------------------------------------------


async def _fail_task(task: TaskModel | TaskBlob, error: Exception) -> None:
    """
    Mark *task* as failed and propagate the update everywhere.

    Accepts either:
      • an ORM TaskModel instance (worker / DB paths), or
      • the raw TaskBlob dict (gateway / scheduler paths).
    """
    finished = time.time()

    # ── normalise to ORM row ─────────────────────────────────────────
    if isinstance(task, TaskModel):
        orm_task = task
    else:  # raw JSON → ORM
        orm_task = TaskModel(**task)

    orm_task.status = Status.failed
    orm_task.result = {"error": str(error)}
    orm_task.last_modified = finished

    # ── build the wire-level dict ───────────────────────────────────
    blob: TaskBlob = {
        "id": str(orm_task.id),
        "pool": orm_task.pool,
        "payload": orm_task.payload or {},
        "labels": orm_task.labels or [],
        "status": orm_task.status,
        "result": orm_task.result,
        "last_modified": orm_task.last_modified,
    }

    # ── fan-out: Redis cache ▸ Postgres ▸ WS subscribers ────────────
    await _save_task(blob)
    await _persist(orm_task)
    await _publish_task(blob)


async def _save_task(task: TaskBlob) -> None:
    """
    Upsert *task* into Redis and refresh its TTL.

    The hash stores:
      • "blob"   – the canonical JSON-encoded task dictionary
      • "status" – lightweight index for quick status look-ups
    """
    key = _task_key(task["id"])
    # Serialise once; no model_dump / extra handling required
    blob = json.dumps(task, default=str)
    status_val = str(task.get("status", ""))  # tolerate absent status
    await queue.hset(key, mapping={"blob": blob, "status": status_val})
    await queue.expire(key, TASK_TTL)


async def _load_task(tid: str) -> TaskBlob | None:
    """
    Fetch a single task from Redis by id.

    Returns:
        • dict  – if the task hash exists
        • None  – if the key is missing or blob field absent
    """
    data = await queue.hget(_task_key(tid), "blob")
    return json.loads(data) if data else None


async def _select_tasks(selector: str) -> list[TaskBlob]:
    """
    Resolve *selector* into concrete task dictionaries.

    Selector formats:
      • task-id            – exact match
      • label:<labelname>  – all tasks whose `labels` contain <labelname>
    """
    if selector.startswith("label:"):
        label = selector.split(":", 1)[1]
        tasks: list[TaskBlob] = []
        for key in await queue.keys("task:*"):
            blob = await queue.hget(key, "blob")
            if not blob:
                continue
            task = json.loads(blob)
            if label in task.get("labels", []):
                tasks.append(task)
        return tasks

    single = await _load_task(selector)
    return [single] if single else []


# ──────────────────────   Results Backend ────────────────────────


# ------------------------------------------------------------------
#  _persist  –  ORM-only implementation (no CRUD schemas, no service layer)
# ------------------------------------------------------------------


async def _persist(task: TaskModel | dict) -> None:
    """
    Persist a task definition—and its first execution attempt—directly
    to Postgres, and forward the job to any configured result backend.

    Parameters
    ----------
    task : TaskModel | dict
        • TaskModel – already-instantiated ORM row (common in worker code)
        • dict      – raw attributes; will be coerced into TaskModel
    """
    try:
        # ---------- normalise input → TaskModel --------------------
        orm_task: TaskModel
        if isinstance(task, TaskModel):
            orm_task = task
        else:  # raw JSON / DTO
            data = {k: task[k] for k in _ORM_COLUMNS if k in task}
            for col in ("id", "tenant_id", "git_reference_id"):
                if col in data and isinstance(data[col], str):
                    try:
                        data[col] = uuid.UUID(str(data[col]))
                    except ValueError:
                        if col == "tenant_id":
                            data[col] = db_helpers._tenant_uuid(data[col])
            for ts in ("date_created", "last_modified"):
                val = data.get(ts)
                if isinstance(val, (int, float)):
                    data[ts] = db_helpers.dt.datetime.fromtimestamp(
                        val, tz=db_helpers.dt.timezone.utc
                    )
            orm_task = TaskModel(**data)

        log.info("persisting task %s", orm_task.id)

        # ---------- optional external result store ----------------
        if result_backend:
            try:
                await result_backend.store(TaskRunModel.from_task(orm_task))
            except Exception as exc:  # noqa: BLE001
                log.warning("result-backend store failed: %s", exc)

        # ---------- upsert into Postgres --------------------------
        async with Session() as ses:
            existing: TaskModel | None = await ses.get(TaskModel, orm_task.id)

            if existing is None:
                # (a) brand-new task definition
                ses.add(orm_task)
                await ses.flush()  # obtain PK for run record

                run = TaskRunModel(
                    task_id=orm_task.id,
                    status=Status.queued,
                )
                ses.add(run)

            else:
                # (b) update mutable columns on existing definition
                for col in ("git_reference_id", "payload", "note"):
                    setattr(existing, col, getattr(orm_task, col))

            await ses.commit()

    except Exception as exc:  # noqa: BLE001
        log.warning("persist error: %s", exc)


# ──────────────────────   Publish Event  ─────────────────────────
# ------------------------------------------------------------------
# 1. publish an event (unchanged — shown for completeness)
# ------------------------------------------------------------------
async def _publish_event(event_type: str, data: dict) -> None:
    event = {
        "type": event_type,
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "data": data,
    }
    await queue.publish(PUBSUB_TOPIC, json.dumps(event, default=str))


# ------------------------------------------------------------------
# 2. flush Redis state to Postgres + optional result backend
# ------------------------------------------------------------------
async def _flush_state() -> None:
    """Persist every cached task to Postgres, then close the queue client."""
    if not queue:
        return

    keys = await queue.keys("task:*")
    for key in keys:
        blob = await queue.hget(key, "blob")
        if not blob:
            continue

        task_dict = json.loads(blob)

        # Forward to configured result-backend (if any)
        if result_backend:
            try:
                orm_row = TaskModel(**task_dict)
                await result_backend.store(TaskRunModel.from_task(orm_row))
            except Exception as exc:  # noqa: BLE001
                log.warning("result-backend store failed: %s", exc)

    # Gracefully close the Redis/queue client
    if hasattr(queue, "client"):
        await queue.client.aclose()


# ------------------------------------------------------------------
# 3. broadcast a single task update
# ------------------------------------------------------------------
async def _publish_task(task: TaskBlob) -> None:
    data = dict(task)  # shallow copy
    if "duration" in task and task["duration"] is not None:
        data["duration"] = task["duration"]
    await _publish_event("task.update", data)


# ------------------------------------------------------------------
# 4. cascade-complete parent tasks when all children finished
# ------------------------------------------------------------------
async def _finalize_parent_tasks(child_id: str) -> None:
    keys = await queue.keys("task:*")
    for key in keys:
        blob = await queue.hget(key, "blob")
        if not blob:
            continue

        parent = json.loads(blob)
        result_block = parent.get("result") or {}
        children = result_block.get("children") or []

        if child_id not in children:
            continue

        # Check every child’s terminal status
        all_done = True
        for cid in children:
            child = await _load_task(cid)
            if not child:
                all_done = False
                break
            if not Status.is_terminal(Status(child.get("status"))):
                all_done = False
                break

        if all_done and parent.get("status") != Status.success:
            parent["status"] = Status.success
            parent["last_modified"] = time.time()
            await _save_task(parent)
            await _persist(parent)
            await _publish_task(parent)


# ------------------------------------------------------------------
# 5. periodic backlog scanner
# ------------------------------------------------------------------
async def _backlog_scanner(interval: float = 5.0) -> None:
    """Background task: walk the cache and close any dangling parent tasks."""
    log.info("backlog scanner started")
    while True:
        keys = await queue.keys("task:*")
        for key in keys:
            blob = await queue.hget(key, "blob")
            if not blob:
                continue

            task_dict = json.loads(blob)
            result_block = task_dict.get("result") or {}
            for cid in result_block.get("children", []):
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

    def _validate(obj: dict) -> dict:
        if obj.get("id") is None:
            obj["id"] = str(uuid.uuid4())
        req = parse_request(obj)
        PModel = _registry.params_model(req.method)
        if PModel is not None:
            PModel.model_validate(req.params)
        return RPCRequest.model_validate(req.model_dump()).model_dump()

    if isinstance(raw, list):
        payload = [_validate(item) for item in raw]
    else:
        payload = _validate(raw)

    log.debug("RPC in  <- %s", payload)
    pre = await _prevalidate(payload, ip)
    if pre is not None:
        return pre
    resp = await dispatcher.dispatch(payload)

    async def _check_unknown(r: dict, method: str) -> None:
        code = r.get("error", {}).get("code")
        if code in (-32601, -32600):
            if code == -32601:
                r["error"]["data"] = {"method": method}
            async with Session() as session:
                count = await db_helpers.record_unknown_handler(session, ip)
            if count >= BAN_THRESHOLD:
                BANNED_IPS.add(ip)
                async with Session() as session:
                    await db_helpers.mark_ip_banned(session, ip)
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
        content=json.dumps(resp, default=str),
        status_code=status,
        media_type="application/json",
    )


# ─────────────────────────── Scheduler loop ─────────────────────
async def scheduler() -> None:
    sched_log.info("scheduler started")

    async with httpx.AsyncClient(timeout=10, http2=True) as client:
        while True:
            # —— 1. pick the next pool that has queued work ——
            pools = await queue.smembers("pools")
            if not pools:
                await asyncio.sleep(0.25)
                continue

            keys = [f"{READY_QUEUE}:{p}" for p in pools]  # e.g. queue:demo
            res = await queue.blpop(keys, 0.5)  # 0.5-sec poll
            if res is None:
                continue

            queue_key, task_raw = res  # guaranteed tuple
            pool = queue_key.split(":", 1)[1]  # strip prefix
            await _publish_queue_length(pool)

            # —— 2. decode the task blob we just pulled ——
            try:
                task: TaskBlob = json.loads(task_raw)
            except Exception as exc:  # noqa: BLE001
                sched_log.warning("invalid task blob (%s); dropping", exc)
                continue

            action = (task.get("payload") or {}).get("action")
            if not action:
                sched_log.warning(
                    "task %s missing action; marking failed", task.get("id")
                )
                await _fail_task(task, MissingActionError())
                continue

            # —— 3. find a live worker that advertises this action ——
            worker_list = await _live_workers_by_pool(pool)
            target = _pick_worker(worker_list, action)
            if not target:
                sched_log.warning(
                    "no worker for %s:%s, failing %s", pool, action, task.get("id")
                )
                await _fail_task(task, NoWorkerAvailableError(pool, action))
                continue

            # —— 4. fire the WORK_START RPC to the worker ——
            task["status"] = Status.dispatched  # optimistic update
            rpc_req = RPCEnvelope(
                id=str(uuid.uuid4()),
                method=WORK_START,
                params={"task": json.loads(json.dumps(task, default=str))},
            ).model_dump()

            try:
                resp = await client.post(target["url"], json=rpc_req)
                if resp.status_code != 200:
                    raise DispatchHTTPError(resp.status_code)

                # —— 5. record and broadcast the dispatch ——
                await _save_task(task)
                await _persist(task)  # ORM path inside persists to DB
                await _publish_task(task)
                sched_log.info(
                    "dispatch %s → %s (HTTP %d)",
                    task.get("id"),
                    target["url"],
                    resp.status_code,
                )

            except Exception as exc:
                # —— 6. transient failure → re-queue and maybe drop worker ——
                sched_log.warning(
                    "dispatch failed (%s) for %s; re-queueing", exc, task.get("id")
                )
                if "id" in target:
                    await _remove_worker(target["id"])
                await queue.rpush(queue_key, task_raw)  # retry later
                await _publish_queue_length(pool)


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
async def _on_start() -> None:
    log.info("gateway startup initiated")
    if engine.url.get_backend_name() != "sqlite":
        result = migrate_core.alembic_upgrade()
        if not result.get("ok", False):
            error_msg = result.get("error")
            stdout = result.get("stdout", "").strip()
            stderr = result.get("stderr", "").strip()
            log.error(
                "migration failed: %s\nstdout:\n%s\nstderr:\n%s",
                error_msg,
                stdout,
                stderr,
            )
            raise MigrationFailureError(str(error_msg))
        log.info("migrations applied; verifying database schema")
        await db_helpers.ensure_status_enum(engine)
        async with engine.begin() as conn:
            # create missing tables if migrations provided none
            await conn.run_sync(Base.metadata.create_all)
    else:
        async with engine.begin() as conn:
            # run once – creates task_runs if it doesn't exist
            await conn.run_sync(Base.metadata.create_all)
        log.info("SQLite metadata initialized (migrations skipped)")

    async with Session() as session:
        banned = await db_helpers.fetch_banned_ips(session)
    BANNED_IPS.update(banned)

    # Load RPC handlers now that dependencies are ready
    from .rpc import initialize
    rpc_modules = initialize()

    log.info("database migrations complete")
    asyncio.create_task(scheduler())
    asyncio.create_task(_backlog_scanner())
    log.info("scheduler and backlog scanner started")
    global READY
    READY = True
    log.info("gateway startup complete")


async def _on_shutdown() -> None:
    log.info("gateway shutdown initiated")
    await _flush_state()
    log.info("state flushed to persistent storage")
    await engine.dispose()
    log.info("database connections closed")


app.add_event_handler("startup", _on_start)
app.add_event_handler("shutdown", _on_shutdown)


# expose RPC handlers lazily to avoid circular imports
__all__ = [
    "keys_upload",
    "keys_fetch",
    "keys_delete",
    "pool_create",
    "pool_join",
    "pool_list",
    "task_submit",
    "task_cancel",
    "task_pause",
    "task_resume",
    "task_retry",
    "task_retry_from",
    "guard_set",
    "secrets_add",
    "secrets_get",
    "secrets_delete",
    "task_patch",
    "task_get",
    "worker_register",
    "worker_heartbeat",
    "worker_list",
    "work_finished",
    "Status",
]


def __getattr__(name: str):
    if name in __all__:
        from .rpc import keys, pool, secrets, tasks, workers

        modules = {
            "keys_upload": keys,
            "keys_fetch": keys,
            "keys_delete": keys,
            "pool_create": pool,
            "pool_join": pool,
            "pool_list": pool,
            "task_submit": tasks,
            "task_cancel": tasks,
            "task_pause": tasks,
            "task_resume": tasks,
            "task_retry": tasks,
            "task_retry_from": tasks,
            "guard_set": tasks,
            "secrets_add": secrets,
            "secrets_get": secrets,
            "secrets_delete": secrets,
            "task_patch": tasks,
            "task_get": tasks,
            "worker_register": workers,
            "worker_heartbeat": workers,
            "worker_list": workers,
            "work_finished": workers,
        }
        module = modules[name]
        return getattr(module, name)
    raise AttributeError(name)
