"""
peagen.gateway
──────────────
FastAPI + AutoAPI JSON-RPC gateway with schema-driven task scheduling.

This file assumes:
• Updated ORM (Task v3, Worker heartbeat via Workers.update)
• Schema-only hooks in gateway/api/hooks/*
• Helper functions in gateway/scheduler_helper.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid


# ─────────── Peagen internals ──────────────────────────────────────────
from autoapi.v2 import AutoAPI, Phase
from auto_authn.v2.providers import RemoteAuthNAdapter
from fastapi import FastAPI, Request

from peagen._utils.config_loader import resolve_cfg
from peagen.core import migrate_core
from peagen.defaults import (
    READY_QUEUE,
)
from peagen.gateway.runtime_cfg import settings
from peagen.errors import MigrationFailureError, NoWorkerAvailableError

# peagen/gateway/__init__.py
from peagen.orm import (
    Base,
    DeployKey,
    Org,
    Pool,
    RawBlob,
    Repository,
    Role,
    RoleGrant,
    RolePerm,
    RepoSecret,
    Task,
    Tenant,
    User,
    UserRepository,
    Work,
    Worker,
)
from peagen.orm import Status as StatusEnum  # noqa: F401
from peagen.plugins import PluginManager
from peagen.plugins.queues import QueueBase
from swarmauri_standard.loggers.Logger import Logger

from . import _publish, schedule_helpers
from .db import engine, get_async_db  # same module as before
from .ws_server import router as ws_router
from sqlalchemy.exc import IntegrityError

# ─────────── logging setup ─────────────────────────────────────────────
LOG_LEVEL = os.getenv("DQ_LOG_LEVEL", "INFO").upper()
log = Logger(name="gw", default_level=getattr(logging, LOG_LEVEL, logging.INFO))
sched_log = Logger(
    name="scheduler", default_level=getattr(logging, LOG_LEVEL, logging.INFO)
)
logging.getLogger("httpx").setLevel("WARNING")
logging.getLogger("uvicorn.error").setLevel("INFO")

# ─────────── FastAPI & AutoAPI initialisation ─────────────────────────
READY: bool = False
app = FastAPI(title="Peagen Pool-Manager Gateway")

authn_adapter = RemoteAuthNAdapter(
    base_url=settings.authn_base_url,
    timeout=settings.authn_timeout,
    cache_ttl=settings.authn_cache_ttl,
    cache_size=settings.authn_cache_size,
)

api = AutoAPI(
    base=Base,
    include={
        Tenant,
        User,
        Org,
        Role,
        RoleGrant,
        RolePerm,
        Repository,
        UserRepository,
        RepoSecret,
        DeployKey,
        Pool,
        Worker,
        Task,
        Work,
        RawBlob,
    },
    get_async_db=get_async_db,
    authn=authn_adapter,
)


@api.hook(Phase.PRE_TX_BEGIN)
async def _shadow_principal(ctx):
    p = getattr(ctx["request"].state, "principal", None)
    if not p:
        return
    db = ctx["db"]
    tid = p.get("tid")
    uid = p.get("sub")
    if not tid or not uid:
        return
    try:
        tid = uuid.UUID(str(tid))
        uid = uuid.UUID(str(uid))
    except (ValueError, AttributeError):
        return
    slug = p.get("tenant_slug") or p.get("tenant") or str(tid)
    if await db.get(Tenant, tid) is None:
        db.add(
            Tenant(
                id=tid,
                slug=slug,
                name=p.get("tenant_name"),
                email=p.get("tenant_email"),
            )
        )
    if await db.get(User, uid) is None:
        db.add(User(id=uid, tenant_id=tid, username=p.get("username") or str(uid)))
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()


# ensure our hook runs second after the AuthN injection hook
_pre = api._hook_registry[Phase.PRE_TX_BEGIN][None]
if _shadow_principal in _pre:
    _pre.remove(_shadow_principal)
_pre.insert(1, _shadow_principal)


app.include_router(api.router)
app.include_router(ws_router)

# ─────────── Plugin-driven queue / result backend ─────────────────────
cfg = resolve_cfg()
plugins = PluginManager(cfg)
queue_plugin = plugins.get("queues", None)
queue: QueueBase = (
    queue_plugin.get_client() if hasattr(queue_plugin, "get_client") else queue_plugin
)

# ─────────── OpenAPI tags configuration ─────────────────────────────────
# Extract all unique tags from routes and sort them alphabetically
all_tags = set()
for route in app.routes:
    if hasattr(route, "tags"):
        all_tags.update(route.tags)

# Update the OpenAPI schema with sorted tags
app.openapi_tags = [{"name": tag} for tag in sorted(all_tags)]


# ─────────── flush Redis state on shutdown ────────────────────────────
async def _flush_state() -> None:
    if not queue:
        return
    keys = await queue.keys("task:*")
    for key in keys:
        _ = await queue.hget(key, "blob")
    if hasattr(queue, "client"):
        await queue.client.aclose()


# ─────────── backlog scanner (parent-completion) ──────────────────────
async def _backlog_scanner(interval: float = 5.0) -> None:
    log.info("backlog-scanner started")
    while True:
        for key in await queue.keys("task:*"):
            blob = await queue.hget(key, "blob")
            if not blob:
                continue
            task = json.loads(blob)
            for cid in task.get("result", {}).get("children", []):
                await schedule_helpers._finalize_parent_tasks(queue, cid)
        await asyncio.sleep(interval)


# ─────────── client IP helper (unchanged) ─────────────────────────────
def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.headers.get("x-real-ip") or request.client.host


# ─────────── scheduler loop ───────────────────────────────────────────
async def scheduler() -> None:
    sched_log.info("scheduler loop started")
    while True:
        # — 1. find pools with queued work
        pools = await queue.smembers("pools")
        if not pools:
            await asyncio.sleep(0.25)
            continue
        # — 2. BLPOP from all pool queues
        keys = [f"{READY_QUEUE}:{p}" for p in pools]
        res = await queue.blpop(keys, 0.5)
        if res is None:
            continue
        queue_key, raw_json = res
        pool = queue_key.split(":", 1)[1]
        await _publish._publish_queue_length(queue, pool)

        try:
            task = Task.model_validate_json(raw_json)
        except Exception as exc:  # noqa: BLE001
            sched_log.warning("invalid task JSON; %s", exc)
            continue

        # — 3. find available worker
        workers = await schedule_helpers.get_live_workers_by_pool(queue, pool)
        target = schedule_helpers.pick_worker(workers, task.action)

        if target is None:
            sched_log.warning("no worker for %s:%s", pool, task.action)
            await schedule_helpers._fail_task(
                task, NoWorkerAvailableError(pool, task.action), sched_log
            )
            continue

        # — 4. dispatch
        ok = await schedule_helpers.dispatch_work(task, target, sched_log)
        if ok:
            await schedule_helpers._save_task(
                queue, task.model_copy(update={"status": StatusEnum.DISPATCHED})
            )
            await _publish._publish_task(queue, task)
        else:
            await schedule_helpers.remove_worker(queue, target["id"])
            await queue.rpush(queue_key, raw_json)  # re-queue
            await asyncio.sleep(1)  # back-off


# ─────────── FastAPI startup / shutdown handlers ──────────────────────
async def _startup() -> None:
    log.info("gateway startup …")

    # 1 – metadata validation / SQLite convenience mode
    await api.initialize_async()

    # 2 – run Alembic first so the ORM never creates tables implicitly
    if engine.url.get_backend_name() != "sqlite":
        mig = migrate_core.alembic_upgrade(
            # keep the exact credentials that were used to build the engine
            db_url=engine.url.render_as_string(hide_password=False)
        )
        if not mig.get("ok"):
            # expose full stderr in logs for easier debugging
            log.error("Alembic failed:\n%s", mig.get("stderr", ""))
            raise MigrationFailureError(mig["error"])

    # 3 – background tasks
    asyncio.create_task(scheduler())
    asyncio.create_task(_backlog_scanner())
    global READY
    READY = True
    log.info("gateway ready")


async def _shutdown() -> None:
    log.info("gateway shutdown …")
    await _flush_state()
    await engine.dispose()


app.add_event_handler("startup", _startup)
app.add_event_handler("shutdown", _shutdown)
