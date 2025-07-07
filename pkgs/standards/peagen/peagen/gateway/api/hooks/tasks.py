from __future__ import annotations

import json
from typing import Any, Dict

from autoapi.v2 import Phase

from peagen.errors import TaskNotFoundError
from peagen.handlers import control_handler
from peagen.transport import (
    TASK_CANCEL,
    TASK_PAUSE,
    TASK_RESUME,
    TASK_RETRY,
    TASK_RETRY_FROM,
)
from peagen.transport.jsonrpc import RPCException
from peagen.transport.jsonrpc_schemas import Status
from peagen.transport.jsonrpc_schemas.task import (
    CountResult,
    SimpleSelectorParams,
)

from .. import (
    READY_QUEUE,
    TASK_TTL,
    _finalize_parent_tasks,
    _live_workers_by_pool,
    _load_task,
    _publish_queue_length,
    _publish_task,
    _save_task,
    _select_tasks,
    log,
    queue,
)
from . import _normalise_submit_payload, _prepare_orm_task, api, dispatcher

# ------------------------------------------------------------------------
# Task CRUD operation hooks
# ------------------------------------------------------------------------


@api.hook(Phase.PRE_TX_BEGIN, method="tasks.create")
async def pre_task_create(ctx: Dict[str, Any]) -> None:
    """Pre-hook for task creation: Normalize payload and check worker availability."""
    params = ctx["env"].params

    # Normalize task payload
    if hasattr(params, "task"):
        task_data = dict(params.task)
    else:
        extra = getattr(params, "__pydantic_extra__", {}) or {}
        task_data = {
            "id": params.id,
            "tenant_id": extra.get("tenant_id"),
            "git_reference_id": extra.get("git_reference_id"),
            "pool": params.pool,
            "payload": params.payload,
            "status": params.status,
            "note": params.note or "",
            "labels": params.labels or [],
            "spec_hash": extra.get("spec_hash"),
            "last_modified": extra.get("last_modified"),
        }

    # Normalize the task data
    task_blob = _normalise_submit_payload(task_data)

    # Shadow-repo guarantees
    payload = task_blob["payload"] or {}
    repo_url = payload.get("repo")
    deploy_key = payload.get("deploy_key")

    if repo_url and deploy_key:
        try:
            from peagen._utils._split_github import _split_github
            from peagen.core.git_shadow_core import (
                attach_deploy_key,
                ensure_mirror,
                ensure_org,
            )

            org, repo = _split_github(repo_url)
            slug = org.lower()

            await ensure_org(slug)
            await ensure_mirror(slug, repo, repo_url)
            key_id = await attach_deploy_key(slug, repo, deploy_key, rw=True)

            payload["deploy_key_id"] = key_id
            task_blob["payload"] = payload
        except Exception as exc:
            log.error("shadow-repo setup failed: %s", exc, exc_info=True)
            raise RPCException(code=-32011, message="shadow-repo setup error")

    # Verify worker availability
    action = payload.get("action")
    if action:
        advertised = {
            h
            for w in await _live_workers_by_pool(task_blob["pool"])
            for h in (
                json.loads(w.get("handlers", "[]"))
                if isinstance(w.get("handlers"), str)
                else w.get("handlers", [])
            )
        }
        if action not in advertised:
            log.warning("no worker advertising '%s' found", action)

    # Store in context for post-hook
    ctx["task_blob"] = task_blob
    ctx["db_task"] = _prepare_orm_task(task_blob)


@api.hook(Phase.POST_COMMIT, method="tasks.create")
async def post_task_create(ctx: Dict[str, Any]) -> None:
    """Post-hook for task creation: Enqueue task and publish events."""
    task_blob = ctx["task_blob"]
    result = ctx["result"]

    # Ensure task ID is correct (may have been generated during persistence)
    task_blob["id"] = result["id"]

    # Enqueue in Redis for processing
    await queue.rpush(
        f"{READY_QUEUE}:{task_blob['pool']}", json.dumps(task_blob, default=str)
    )

    # Update cache and publish events
    await queue.sadd("pools", task_blob["pool"])
    await _publish_queue_length(task_blob["pool"])
    await _save_task(task_blob)
    await _publish_task(task_blob)

    log.info(
        "task %s queued in %s (ttl=%ss)", task_blob["id"], task_blob["pool"], TASK_TTL
    )


@api.hook(Phase.PRE_TX_BEGIN, method="tasks.update")
async def pre_task_update(ctx: Dict[str, Any]) -> None:
    """Pre-hook for task updates: Load existing task from cache."""
    params = ctx["env"].params
    task_id = params.get("id") or params.get("item_id")
    changes = params.get("changes", {})

    task = await _load_task(task_id)
    if not task:
        raise TaskNotFoundError(task_id)

    # Store the current task in context
    ctx["current_task"] = task
    ctx["changes"] = changes


@api.hook(Phase.POST_COMMIT, method="tasks.update")
async def post_task_update(ctx: Dict[str, Any]) -> None:
    """Post-hook for task updates: Update cache and publish events."""
    task = ctx["current_task"]
    changes = ctx["changes"]

    # Apply changes to the task
    for field, value in changes.items():
        if field == "status":
            value = Status(value)
        task[field] = value

    # Update cache and publish
    await _save_task(task)
    await _publish_task(task)

    # Check if we need to finalize parent tasks
    if isinstance(changes.get("result"), dict):
        for cid in changes["result"].get("children", []):
            await _finalize_parent_tasks(cid)

    log.info("task %s updated with %s", task["id"], ",".join(changes.keys()))


@api.hook(Phase.PRE_TX_BEGIN, method="tasks.read")
async def pre_task_read(ctx: Dict[str, Any]) -> None:
    """Pre-hook for task read: Check cache before database."""
    params = ctx["env"].params
    task_id = params.get("id") or params.get("item_id")

    task = await _load_task(task_id)
    if task:
        # If we found it in cache, store it in context
        ctx["cached_task"] = task
        ctx["skip_db"] = True  # Signal to skip database lookup


@api.hook(Phase.POST_HANDLER, method="tasks:read")
async def post_task_read(ctx: Dict[str, Any]) -> None:
    """Post-hook for task read: Use cached task if available."""
    if ctx.get("skip_db") and ctx.get("cached_task"):
        # Replace result with cached task
        ctx["result"] = ctx["cached_task"]


# ------------------------------------------------------------------------
# Custom operations that don't map directly to CRUD
# ------------------------------------------------------------------------


@dispatcher.method(TASK_CANCEL)
async def task_cancel(params: SimpleSelectorParams) -> CountResult:
    selector = params.selector
    targets = await _select_tasks(selector)
    count = await control_handler.apply("cancel", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("cancel %s -> %d tasks", selector, count)
    return CountResult(count=count)


@dispatcher.method(TASK_PAUSE)
async def task_pause(params: SimpleSelectorParams) -> CountResult:
    selector = params.selector
    targets = await _select_tasks(selector)
    count = await control_handler.apply("pause", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("pause %s -> %d tasks", selector, count)
    return CountResult(count=count)


@dispatcher.method(TASK_RESUME)
async def task_resume(params: SimpleSelectorParams) -> CountResult:
    selector = params.selector
    targets = await _select_tasks(selector)
    count = await control_handler.apply("resume", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("resume %s -> %d tasks", selector, count)
    return CountResult(count=count)


@dispatcher.method(TASK_RETRY)
async def task_retry(params: SimpleSelectorParams) -> CountResult:
    selector = params.selector
    targets = await _select_tasks(selector)
    count = await control_handler.apply("retry", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("retry %s -> %d tasks", selector, count)
    return CountResult(count=count)


@dispatcher.method(TASK_RETRY_FROM)
async def task_retry_from(params: SimpleSelectorParams) -> CountResult:
    selector = params.selector
    targets = await _select_tasks(selector)
    count = await control_handler.apply(
        "retry_from", queue, targets, READY_QUEUE, TASK_TTL
    )
    log.info("retry_from %s -> %d tasks", selector, count)
    return CountResult(count=count)


# ───────── task helpers (hash + ttl) ────────────────────────────


def _task_key(tid: str) -> str:
    return TASK_KEY.format(tid)




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
