"""
peagen.gateway
──────────────
FastAPI + Tigrbl JSON-RPC gateway with schema-driven task scheduling.

This file assumes:
• Updated ORM (Task v3, Worker heartbeat via Worker.update)
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
from tigrbl import TigrblApp, get_schema
from tigrbl_auth.adapters import RemoteAuthNAdapter
from fastapi import Request

from peagen._utils.config_loader import resolve_cfg
from peagen.core import migrate_core
from peagen.defaults import (
    READY_QUEUE,
)
from peagen.gateway.runtime_cfg import settings
from peagen.errors import MigrationFailureError, NoWorkerAvailableError

# peagen/gateway/__init__.py
from peagen.orm import (
    DeployKey,
    PublicKey,
    GPGKey,
    Org,
    Pool,
    RawBlob,
    Repository,
    # Role,
    # RoleGrant,
    # RolePerm,
    RepoSecret,
    Worker,
    Task,
    Tenant,
    User,
    UserRepository,
    Work,
)
from peagen.orm import Status as StatusEnum  # noqa: F401
from peagen.plugins import PluginManager
from peagen.plugins.queues import QueueBase
from swarmauri_standard.loggers.Logger import Logger

from . import _publish, schedule_helpers
from .db import ENGINE
from .ws_server import router as ws_router
from sqlalchemy.exc import IntegrityError


# ─────────── shadow principal hook ─────────────────────────────────────
async def _shadow_principal(ctx):
    import logging
    from fastapi import HTTPException
    from peagen.orm import User

    log = logging.getLogger(__name__)

    p = getattr(ctx["request"].state, "principal", None)
    if not p:
        log.info("shadow_principal: no principal on request")
        return

    tid = p.get("tid")
    uid = p.get("sub")
    if not tid or not uid:
        log.info("shadow_principal: missing tid or sub in principal: %s", p)
        return

    try:
        tid = uuid.UUID(str(tid))
        uid = uuid.UUID(str(uid))
    except (ValueError, AttributeError):
        log.info("shadow_principal: invalid UUIDs tid=%s sub=%s", tid, uid)
        return

    username = p.get("username") or str(uid)
    db = ctx["db"]

    UReadIn = get_schema(User, op="delete")
    UUpdateIn = get_schema(User, op="update")
    UCreateIn = get_schema(User, op="create")

    def _is_duplicate(exc: Exception) -> bool:
        if isinstance(exc, IntegrityError):
            return True
        if isinstance(exc, HTTPException) and getattr(exc, "status_code", None) == 409:
            return True
        msg = (getattr(exc, "detail", "") or str(exc)).lower()
        return "duplicate key" in msg or "already exists" in msg

    def _upsert_sync(s):
        log.info("shadow_principal: upsert start uid=%s tid=%s", uid, tid)

        exists = False
        try:
            app.methods.User.read(UReadIn(id=uid), db=s)
            exists = True
            log.info("shadow_principal: user exists uid=%s", uid)
        except Exception as exc:
            if s.in_transaction():
                s.rollback()
            log.info("shadow_principal: User.read miss uid=%s (%s)", uid, exc)

        if exists:
            upd = UUpdateIn(id=uid, tenant_id=tid, username=username, is_active=True)
            log.info("shadow_principal: updating uid=%s", uid)
            return app.methods.User.update(upd, db=s)

        try:
            cre = UCreateIn(id=uid, tenant_id=tid, username=username, is_active=True)
            log.info("shadow_principal: creating uid=%s", uid)
            return app.methods.User.create(cre, db=s)
        except Exception as exc:
            if _is_duplicate(exc):
                if s.in_transaction():
                    s.rollback()
                log.info("shadow_principal: create raced, retrying update uid=%s", uid)
                upd = UUpdateIn(
                    id=uid, tenant_id=tid, username=username, is_active=True
                )
                return app.methods.User.update(upd, db=s)
            raise

    try:
        if hasattr(db, "run_sync"):
            await db.run_sync(_upsert_sync)
        else:
            _upsert_sync(db)
    except Exception as exc:
        log.info("shadow_principal: upsert failed uid=%s err=%s", uid, exc)


# ─────────── logging setup ─────────────────────────────────────────────
LOG_LEVEL = os.getenv("PEAGEN_LOG_LEVEL", "INFO").upper()
log = Logger(name="gw", default_level=getattr(logging, LOG_LEVEL, logging.INFO))
sched_log = Logger(
    name="scheduler", default_level=getattr(logging, LOG_LEVEL, logging.INFO)
)
logging.getLogger("httpx").setLevel("WARNING")
logging.getLogger("uvicorn.error").setLevel("INFO")

# ─────────── TigrblApp initialisation ─────────────────────────
READY: bool = False
app = TigrblApp(
    title="Peagen Pool-Manager Gateway",
    engine=ENGINE,
    api_hooks={"PRE_TX_BEGIN": [_shadow_principal]},
)
authn_adapter = RemoteAuthNAdapter(
    base_url=settings.authn_base_url,
    timeout=settings.authn_timeout,
    cache_ttl=settings.authn_cache_ttl,
    cache_size=settings.authn_cache_size,
)

app.set_auth(
    authn=authn_adapter.get_principal,
    optional_authn_dep=authn_adapter.get_principal_optional,
    allow_anon=False,
)
app.include_models(
    [
        Tenant,
        User,
        Org,
        # Role,
        # RoleGrant,
        # RolePerm,
        Repository,
        UserRepository,
        RepoSecret,
        DeployKey,
        PublicKey,
        GPGKey,
        Pool,
        Worker,
        Task,
        Work,
        RawBlob,
    ]
)

app.mount_jsonrpc(prefix="/rpc")
app.attach_diagnostics(prefix="/system")

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
    await app.initialize()

    # 2 – run Alembic first so the ORM never creates tables implicitly
    eng, _ = ENGINE.raw()
    if eng.url.get_backend_name() != "sqlite":
        mig = migrate_core.alembic_upgrade(
            # keep the exact credentials that were used to build the engine
            db_url=eng.url.render_as_string(hide_password=False)
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
    log.info(app.router)
    log.info(app.rpc)
    log.info(app.models)
    log.info(app.schemas)
    log.info(app._allow_anon)

    log.info("gateway ready")


async def _shutdown() -> None:
    log.info("gateway shutdown …")
    await _flush_state()
    eng, _ = ENGINE.raw()
    await eng.dispose()


app.add_event_handler("startup", _startup)
app.add_event_handler("shutdown", _shutdown)

__all__ = ["app"]
