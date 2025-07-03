"""
AutoAPI hooks for task-related operations.
"""

import json
import uuid
from typing import Any, Dict

from peagen._utils._split_github import _split_github
from peagen.core.git_shadow_core import (
    attach_deploy_key,
    ensure_mirror,
    ensure_org,
)
from peagen.transport.jsonrpc import RPCException
from peagen.transport.jsonrpc_schemas import Status

from ... import (
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
from ...autoapi import api
from ...rpc.tasks import _normalise_submit_payload

# ---------------------- Task Create Hooks ----------------------


@api.hook(api.Phase.PRE_TX_BEGIN, method="tasks.create")
async def pre_task_create(ctx: Dict[str, Any]) -> None:
    """Pre-processing for task creation"""
    params = ctx.get("env").params

    # 1. Normalize the submit payload
    if "task" in params:
        task_blob = _normalise_submit_payload(dict(params["task"]))
    else:
        base = {
            "id": params.get("id"),
            "tenant_id": params.get("tenant_id"),
            "git_reference_id": params.get("git_reference_id"),
            "pool": params.get("pool", "default"),
            "payload": params.get("payload", {}),
            "status": params.get("status", Status.queued),
            "note": params.get("note", ""),
            "labels": params.get("labels", []),
            "spec_hash": params.get("spec_hash"),
            "last_modified": params.get("last_modified"),
        }
        task_blob = _normalise_submit_payload(base)

    # Store in context for later hooks
    ctx["task_blob"] = task_blob

    # Register pool
    await queue.sadd("pools", task_blob["pool"])

    # 2. Shadow-repo guarantees
    payload = task_blob["payload"] or {}
    repo_url = payload.get("repo")
    deploy_key = payload.get("deploy_key")

    if repo_url and deploy_key:
        try:
            org, repo = _split_github(repo_url)
            slug = org.lower()

            await ensure_org(slug)
            await ensure_mirror(slug, repo, repo_url)
            key_id = await attach_deploy_key(slug, repo, deploy_key, rw=True)

            # Update payload with deploy key ID
            payload["deploy_key_id"] = key_id
            task_blob["payload"] = payload

            # Update params for persistence
            params_dict = dict(params)
            if "task" in params_dict:
                params_dict["task"]["payload"] = payload
            else:
                params_dict["payload"] = payload
            ctx["env"].params = params_dict

        except Exception as exc:
            log.error("shadow-repo setup failed: %s", exc, exc_info=True)
            raise RPCException(code=-32011, message="shadow-repo setup error")

    # 3. Verify worker advertises action
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

    # 4. Avoid ID collision
    if await _load_task(task_blob["id"]):
        new_id = uuid.uuid4().hex
        task_blob["id"] = new_id

        # Update the ID in params
        if "task" in params:
            params["task"]["id"] = new_id
        else:
            params["id"] = new_id

        log.warning("task id collision – generated new id %s", new_id)


@api.hook(api.Phase.POST_COMMIT, method="tasks.create")
async def post_task_create(ctx: Dict[str, Any]) -> None:
    """Post-commit operations for task creation"""
    result = ctx.get("result")
    task_blob = ctx.get("task_blob")

    if not result or not task_blob:
        return

    # Make sure task_blob has the correct ID from the result
    task_blob["id"] = str(result["id"])

    # 6. Enqueue & broadcast
    await queue.rpush(
        f"{READY_QUEUE}:{task_blob['pool']}", json.dumps(task_blob, default=str)
    )
    await _publish_queue_length(task_blob["pool"])
    await _save_task(task_blob)
    await _publish_task(task_blob)

    log.info(
        "task %s queued in %s (ttl=%ss)", task_blob["id"], task_blob["pool"], TASK_TTL
    )


# ---------------------- Task Update Hooks ----------------------


@api.hook(api.Phase.PRE_TX_BEGIN, method="tasks.update")
async def pre_task_update(ctx: Dict[str, Any]) -> None:
    """Pre-processing for task update"""
    params = ctx.get("env").params
    task_id = params.get("id")
    changes = params.get("changes", {})

    # Load the task from Redis
    task = await _load_task(task_id)
    if not task:
        raise RPCException(code=-32000, message=f"Task not found: {task_id}")

    # Store original task for later
    ctx["original_task"] = task
    ctx["changes"] = changes


@api.hook(api.Phase.POST_COMMIT, method="tasks.update")
async def post_task_update(ctx: Dict[str, Any]) -> None:
    """Post-commit operations for task update"""
    result = ctx.get("result")
    original_task = ctx.get("original_task")
    changes = ctx.get("changes")

    if not result or not original_task:
        return

    # Update the task with changes from the result
    updated_task = dict(original_task)
    for k, v in result.items():
        updated_task[k] = v

    # Save to Redis and publish updates
    await _save_task(updated_task)
    await _publish_task(updated_task)

    # Cascade completion checks if needed
    if isinstance(changes.get("result"), dict):
        for cid in changes["result"].get("children", []):
            await _finalize_parent_tasks(cid)

    log.info("task %s patched with %s", updated_task["id"], ",".join(changes.keys()))


# ---------------------- Task Delete Hooks ----------------------


@api.hook(api.Phase.POST_COMMIT, method="tasks.delete")
async def post_task_delete(ctx: Dict[str, Any]) -> None:
    """Post-commit operations for task deletion"""
    result = ctx.get("result")
    if not result or "id" not in result:
        return

    task_id = result["id"]

    # Remove from Redis
    await queue.delete(f"task:{task_id}")

    # Publish deletion event
    await _publish_task({"id": task_id, "status": "deleted"})

    log.info("task %s deleted", task_id)
