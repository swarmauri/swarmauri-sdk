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
from peagen.errors import (
    DispatchHTTPError,
    MigrationFailureError,
    MissingActionError,
    NoWorkerAvailableError,
)
from peagen.plugins import PluginManager
from peagen.plugins.queues import QueueBase
from swarmauri_standard.loggers.Logger import Logger


from autoapi.v2 import AutoAPI
from peagen.gateway.db import get_async_db

from peagen.gateway.ws_server import router as ws_router


TaskBlob = Dict[str, Any]

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
READY = False

app = FastAPI(title="Peagen Pool Manager Gateway")

# Initialize AutoAPI with our models
api = AutoAPI(
    base=Base,
    include={TaskModel, WorkerModel, PoolModel, SecretModel, DeployKeyModel},
    get_async_db=get_async_db,
)

app.include_router(api.router)
app.include_router(ws_router)

cfg = resolve_cfg()
CONTROL_QUEUE = cfg.get("control_queue", defaults.CONFIG["control_queue"])
READY_QUEUE = cfg.get("ready_queue", defaults.CONFIG["ready_queue"])
PUBSUB_TOPIC = cfg.get("pubsub", defaults.CONFIG["pubsub"])
pm = PluginManager(cfg)

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

