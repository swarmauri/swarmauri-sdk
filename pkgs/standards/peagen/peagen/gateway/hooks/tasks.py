"""
gateway.hooks.task
────────────────────────────────────────────────────────
AutoAPI-compatible Task hooks (schemas only, no TaskBlob).
"""

from __future__ import annotations
import json, time, uuid
from typing import Any, Dict, List

from autoapi.v2 import Phase, AutoAPI
from peagen.orm            import Status, Task
from peagen.transport.jsonrpc import RPCException
from peagen.errors         import TaskNotFoundError
import peagen.defaults as defaults
from peagen.defaults       import READY_QUEUE, TASK_TTL, TASK_KEY

from ..    import log, queue, api
from ..schedule_helpers import _live_workers_by_pool
from .._publish import _publish_task, _publish_event, _publish_queue_length

# ──────────────────────── Schema handles ──────────────────────────────
TaskCreate = AutoAPI.get_schema(Task, "create")
TaskRead   = AutoAPI.get_schema(Task, "read")
TaskUpdate = AutoAPI.get_schema(Task, "update")


# ───────────────────────── Queue helpers ──────────────────────────────
def _task_key(tid: str) -> str:
    return TASK_KEY.format(tid)


# ─────────────────────────── CREATE hooks ─────────────────────────────
@api.hook(Phase.PRE_TX_BEGIN, method="Tasks.create")
async def pre_task_create(ctx: Dict[str, Any]) -> None:
    tc: TaskCreate = ctx["env"].params            # validated Pydantic model

    # ---- optional shadow-repo logic -----------------------------------
    args = tc.args or {}
    repo_url   = args.get("repo_url")
    deploy_key = args.get("deploy_key")

    if repo_url and deploy_key:
        try:
            from peagen._utils._split_github import _split_github
            from peagen.core.git_shadow_core import (
                ensure_org, ensure_mirror, attach_deploy_key,
            )
            org, repo = _split_github(repo_url)
            slug = org.lower()
            await ensure_org(slug)
            await ensure_mirror(slug, repo, repo_url)
            key_id = await attach_deploy_key(slug, repo, deploy_key, rw=True)

            args["deploy_key_id"] = key_id
            tc = tc.model_copy(update={"args": args})
        except Exception as exc:      # noqa: BLE001
            log.error("shadow-repo setup failed: %s", exc, exc_info=True)
            raise RPCException(code=-32011, message="shadow-repo setup error")

    # ---- worker-advertising sanity check ------------------------------
    action = tc.action
    if action:
        advertised = {
            h
            for w in await _live_workers_by_pool(tc.pool_id)
            for h in (
                json.loads(w.get("handlers", "[]"))
                if isinstance(w.get("handlers"), str)
                else w.get("handlers", [])
            )
        }
        if action not in advertised:
            log.warning("no worker advertising '%s' found", action)

    ctx["task_in"] = tc                        # cache possibly-mutated model


@api.hook(Phase.POST_COMMIT, method="Tasks.create")
async def post_task_create(ctx: Dict[str, Any]) -> None:
    created: TaskRead  = ctx["result"]
    submitted: TaskCreate = ctx["task_in"]

    wire = submitted.model_copy(update={"id": created.id})  # align IDs

    # push to Redis queue keyed by pool_id
    await queue.rpush(
        f"{READY_QUEUE}:{wire.pool_id}",
        json.dumps(wire.model_dump(mode="json")),
    )
    await queue.sadd("pools", wire.pool_id)
    await _publish_queue_length(wire.pool_id)
    await _save_task(TaskRead.model_validate(wire.model_dump()))
    await _publish_task(wire.model_dump())

    log.info("task %s queued in %s (ttl=%s)", created.id, wire.pool_id, TASK_TTL)


# ─────────────────────────── UPDATE hooks ─────────────────────────────
@api.hook(Phase.PRE_TX_BEGIN, method="Tasks.update")
async def pre_task_update(ctx: Dict[str, Any]) -> None:
    upd: TaskUpdate = ctx["env"].params
    tid             = upd.id or upd.item_id
    cached          = await _load_task(tid)
    if cached is None:
        raise TaskNotFoundError(tid)

    ctx["cached_task"] = cached
    ctx["changes"]     = upd.model_dump(exclude_unset=True)


@api.hook(Phase.POST_COMMIT, method="Tasks.update")
async def post_task_update(ctx: Dict[str, Any]) -> None:
    task: TaskRead          = ctx["cached_task"]
    changes: Dict[str, Any] = ctx["changes"]

    task = task.model_copy(update=changes)      # immutable → new instance
    await _save_task(task)
    await _publish_task(task.model_dump())

    # parent-completion fan-out
    if isinstance(changes.get("result"), dict):
        for cid in changes["result"].get("children", []):
            await _finalize_parent_tasks(cid)

    log.info("task %s updated (%s)", task.id, ", ".join(changes))


# ─────────────────────────── READ hooks ───────────────────────────────
@api.hook(Phase.PRE_TX_BEGIN, method="Tasks.read")
async def pre_task_read(ctx: Dict[str, Any]) -> None:
    tid = ctx["env"].params.get("id") or ctx["env"].params.get("item_id")
    hit = await _load_task(tid)
    if hit:
        ctx["cached_task"] = hit
        ctx["skip_db"]     = True


@api.hook(Phase.POST_HANDLER, method="Tasks.read")
async def post_task_read(ctx: Dict[str, Any]) -> None:
    if ctx.get("skip_db") and ctx.get("cached_task"):
        ctx["result"] = ctx["cached_task"]


# ───────────────────────── Redis helpers ──────────────────────────────
async def _save_task(task: TaskRead) -> None:
    """Upsert *task* (TaskRead model) into Redis and refresh its TTL."""
    key = _task_key(str(task.id))
    blob_json = json.dumps(task.model_dump(mode="json"))
    await queue.hset(
        key,
        mapping={"blob": blob_json, "status": str(task.status)},
    )
    await queue.expire(key, TASK_TTL)


async def _load_task(tid: str) -> TaskRead | None:
    data = await queue.hget(_task_key(tid), "blob")
    return TaskRead.model_validate_json(data) if data else None


# ───────────────────────── misc utilities ─────────────────────────────
async def _finalize_parent_tasks(child_id: str) -> None:
    keys = await queue.keys("task:*")
    for key in keys:
        blob = await queue.hget(key, "blob")
        if not blob:
            continue

        parent = TaskRead.model_validate_json(blob)
        children = parent.result.get("children", []) if parent.result else []

        if child_id not in children:
            continue

        all_done = True
        for cid in children:
            child = await _load_task(cid)
            if child is None or not Status.is_terminal(child.status):
                all_done = False
                break

        if all_done and parent.status != Status.success:
            parent = parent.model_copy(
                update={"status": Status.success, "last_modified": time.time()}
            )
            await _save_task(parent)
            await _publish_task(parent.model_dump())
