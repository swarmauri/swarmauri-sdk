"""
gateway.hooks.task
────────────────────────────────────────────────────────
AutoAPI-compatible Task hooks (schemas only, no TaskBlob).
"""

from __future__ import annotations

import json
from typing import Any, Dict

from autoapi.v2 import AutoAPI, Phase

from peagen.defaults import READY_QUEUE, TASK_TTL
from peagen.errors import TaskNotFoundError
from peagen.orm import Task
from peagen.transport.jsonrpc import RPCException

from peagen.gateway import api, log, queue
from peagen.gateway._publish import _publish_queue_length, _publish_task
from peagen.gateway.schedule_helpers import (
    _finalize_parent_tasks,
    _load_task,
    _save_task,
    get_live_workers_by_pool,
)

# ──────────────────────── Schema handles ──────────────────────────────
TaskCreate = AutoAPI.get_schema(Task, "create")
TaskRead = AutoAPI.get_schema(Task, "read")
TaskUpdate = AutoAPI.get_schema(Task, "update")


# ─────────────────────────── CREATE hooks ─────────────────────────────
@api.hook(Phase.PRE_TX_BEGIN, model="Tasks", op="create")
async def pre_task_create(ctx: Dict[str, Any]) -> None:
    log.info("entering pre_task_create")

    tc: TaskCreate = ctx["env"].params  # validated Pydantic model

    # ---- optional shadow-repo logic -----------------------------------
    args = tc.args or {}
    repo_url = args.get("repo_url")
    deploy_key = args.get("deploy_key")

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

            args["deploy_key_id"] = key_id
            tc = tc.model_copy(update={"args": args})
        except Exception as exc:  # noqa: BLE001
            log.error("shadow-repo setup failed: %s", exc, exc_info=True)
            raise RPCException(code=-32011, message="shadow-repo setup error")

    # ---- worker-advertising sanity check ------------------------------
    action = tc.action
    if action:
        advertised = {
            h
            for w in await get_live_workers_by_pool(queue, tc.pool_id)
            for h in (
                json.loads(w.get("handlers", "[]"))
                if isinstance(w.get("handlers"), str)
                else w.get("handlers", [])
            )
        }
        if action not in advertised:
            log.warning("no worker advertising '%s' found", action)

    ctx["task_in"] = tc  # cache possibly-mutated model


@api.hook(Phase.POST_COMMIT, model="Tasks", op="create")
async def post_task_create(ctx: Dict[str, Any]) -> None:
    log.info("entering post_task_create")

    created: TaskRead = ctx["result"]
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
@api.hook(Phase.PRE_TX_BEGIN, model="Tasks", op="update")
async def pre_task_update(ctx: Dict[str, Any]) -> None:
    log.info("entering pre_task_update")

    upd: TaskUpdate = ctx["env"].params
    tid = upd.id or upd.item_id
    cached = await _load_task(queue, tid)
    if cached is None:
        raise TaskNotFoundError(tid)

    ctx["cached_task"] = cached
    ctx["changes"] = upd.model_dump(exclude_unset=True)


@api.hook(Phase.POST_COMMIT, model="Tasks", op="update")
async def post_task_update(ctx: Dict[str, Any]) -> None:
    log.info("entering post_task_update")

    task: TaskRead = ctx["cached_task"]
    changes: Dict[str, Any] = ctx["changes"]

    task = task.model_copy(update=changes)  # immutable → new instance
    await _save_task(task)
    await _publish_task(task.model_dump())

    # parent-completion fan-out
    if isinstance(changes.get("result"), dict):
        for cid in changes["result"].get("children", []):
            await _finalize_parent_tasks(cid)

    log.info("task %s updated (%s)", task.id, ", ".join(changes))


# ─────────────────────────── READ hooks ───────────────────────────────
@api.hook(Phase.PRE_TX_BEGIN, model="Tasks", op="read")
async def pre_task_read(ctx: Dict[str, Any]) -> None:
    log.info("entering pre_task_read")

    tid = ctx["env"].params.get("id") or ctx["env"].params.get("item_id")
    hit = await _load_task(queue, tid)
    if hit:
        ctx["cached_task"] = hit
        ctx["skip_db"] = True


@api.hook(Phase.POST_HANDLER, model="Tasks", op="read")
async def post_task_read(ctx: Dict[str, Any]) -> None:
    log.info("entering post_task_read")

    if ctx.get("skip_db") and ctx.get("cached_task"):
        ctx["result"] = ctx["cached_task"]
