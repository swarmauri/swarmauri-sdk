"""
gateway.api.hooks.task
────────────────────────────────────────────────────────
Hooks for Task CRUD that rely **only** on AutoAPI-generated schemas.
No hand-rolled “task_blob”, no custom normalise/prepare helpers.
"""

from __future__ import annotations

import json, time, uuid
from typing import Any, Dict, List

from autoapi.v2 import Phase, AutoAPI
from peagen.orm import Status, Task
from peagen.transport.jsonrpc import RPCException
from peagen.errors import TaskNotFoundError
import peagen.defaults as defaults

from .. import (
    READY_QUEUE,
    TASK_TTL,
    _finalize_parent_tasks,
    _live_workers_by_pool,
    _load_task,
    _publish_queue_length,
    _publish_task,
    _save_task,
    log,
    queue,
)
from . import api

# ─────────────────────────── Schema handles ───────────────────────────
TaskCreate = AutoAPI.get_schema(Task, "create")
TaskRead   = AutoAPI.get_schema(Task, "read")
TaskUpdate = AutoAPI.get_schema(Task, "update")


# ─────────────────────────── For Queues ───────────────────────────────
TASK_KEY = defaults.CONFIG["task_key"]

def _task_key(tid: str) -> str:
    return TASK_KEY.format(tid)

# ─────────────────────────── CREATE hooks ─────────────────────────────
@api.hook(Phase.PRE_TX_BEGIN, method="tasks.create")
async def pre_task_create(ctx: Dict[str, Any]) -> None:
    tc: TaskCreate = ctx["env"].params                      # already validated

    # ---- optional shadow-repo logic ----------------------------------
    payload = tc.payload or {}
    repo_url   = payload.get("repo")
    deploy_key = payload.get("deploy_key")

    if repo_url and deploy_key:
        try:
            from peagen._utils._split_github import _split_github
            from peagen.core.git_shadow_core import ensure_org, ensure_mirror, attach_deploy_key

            org, repo = _split_github(repo_url)
            slug = org.lower()
            await ensure_org(slug)
            await ensure_mirror(slug, repo, repo_url)
            key_id = await attach_deploy_key(slug, repo, deploy_key, rw=True)

            payload["deploy_key_id"] = key_id
            tc = tc.model_copy(update={"payload": payload})
        except Exception as exc:  # noqa: BLE001
            log.error("shadow-repo setup failed: %s", exc, exc_info=True)
            raise RPCException(code=-32011, message="shadow-repo setup error")

    # ---- worker-advertising sanity check -----------------------------
    action = payload.get("action")
    if action:
        advertised = {
            h
            for w in await _live_workers_by_pool(tc.pool)
            for h in (
                json.loads(w.get("handlers", "[]"))
                if isinstance(w.get("handlers"), str)
                else w.get("handlers", [])
            )
        }
        if action not in advertised:
            log.warning("no worker advertising '%s' found", action)

    # store the validated – possibly mutated – model for later use
    ctx["task_in"]  = tc


@api.hook(Phase.POST_COMMIT, method="tasks.create")
async def post_task_create(ctx: Dict[str, Any]) -> None:
    created: TaskRead = ctx["result"]               # AutoAPI response model
    tc: TaskCreate    = ctx["task_in"]

    # enqueue to Redis (use model_dump → JSON)
    wire = tc.model_copy(update={"id": created.id})      # ensure ID matches DB
    await queue.rpush(
        f"{READY_QUEUE}:{wire.pool}",
        json.dumps(wire.model_dump(mode="json"), default=str),
    )
    await queue.sadd("pools", wire.pool)
    await _publish_queue_length(wire.pool)
    await _save_task(wire.model_dump(mode="python"))
    await _publish_task(wire.model_dump(mode="python"))

    log.info("task %s queued in %s (ttl=%s)", created.id, wire.pool, TASK_TTL)


# ─────────────────────────── UPDATE hooks ─────────────────────────────
@api.hook(Phase.PRE_TX_BEGIN, method="tasks.update")
async def pre_task_update(ctx: Dict[str, Any]) -> None:
    upd: TaskUpdate = ctx["env"].params
    tid = upd.id or upd.item_id                         # PK may be in either
    cached = await _load_task(tid)
    if not cached:
        raise TaskNotFoundError(tid)

    ctx["cached_task"] = cached
    ctx["changes"]     = upd.model_dump(exclude_unset=True)


@api.hook(Phase.POST_COMMIT, method="tasks.update")
async def post_task_update(ctx: Dict[str, Any]) -> None:
    task = ctx["cached_task"]
    changes: dict[str, Any] = ctx["changes"]

    for k, v in changes.items():
        task[k] = Status(v) if k == "status" else v

    await _save_task(task)
    await _publish_task(task)

    if isinstance(changes.get("result"), dict):
        for cid in changes["result"].get("children", []):
            await _finalize_parent_tasks(cid)

    log.info("task %s updated (%s)", task["id"], ", ".join(changes))


# ─────────────────────────── READ hooks ──────────────────────────────
@api.hook(Phase.PRE_TX_BEGIN, method="tasks.read")
async def pre_task_read(ctx: Dict[str, Any]) -> None:
    tid = ctx["env"].params.get("id") or ctx["env"].params.get("item_id")
    hit = await _load_task(tid)
    if hit:
        ctx["cached_task"] = hit
        ctx["skip_db"]     = True


@api.hook(Phase.POST_HANDLER, method="tasks.read")
async def post_task_read(ctx: Dict[str, Any]) -> None:
    if ctx.get("skip_db") and ctx.get("cached_task"):
        ctx["result"] = ctx["cached_task"]

# ───────── task helpers (hash + ttl) ────────────────────────────

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
    #await _persist(orm_task)
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
            #await _persist(parent)
            await _publish_task(parent)
