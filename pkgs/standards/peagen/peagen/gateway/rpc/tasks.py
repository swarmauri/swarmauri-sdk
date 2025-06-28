from __future__ import annotations

import json
import uuid

from peagen.transport.jsonrpc import RPCException
from peagen.defaults.error_codes import ErrorCode

from .. import (
    log,
    rpc,
    queue,
    READY_QUEUE,
    TASK_TTL,
    _live_workers_by_pool,
    _load_task,
    _persist,
    _publish_queue_length,
    _publish_task,
    _save_task,
    _select_tasks,
    _finalize_parent_tasks,
)
from ..errors import TaskNotFoundError
from ..orm.status import Status
from ..orm import Task


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
    await queue.sadd("pools", pool)

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

    await queue.rpush(f"{READY_QUEUE}:{pool}", task.model_dump_json())
    await _publish_queue_length(pool)
    await _save_task(task)
    await _persist(task)
    await _publish_task(task)

    log.info("task %s queued in %s (ttl=%ss)", task.id, pool, TASK_TTL)
    return {"taskId": task.id}


@rpc.method("Task.cancel")
async def task_cancel(selector: str) -> dict:
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("cancel", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("cancel %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Task.pause")
async def task_pause(selector: str) -> dict:
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("pause", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("pause %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Task.resume")
async def task_resume(selector: str) -> dict:
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("resume", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("resume %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Task.retry")
async def task_retry(selector: str) -> dict:
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("retry", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("retry %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Task.retry_from")
async def task_retry_from(selector: str) -> dict:
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply(
        "retry_from", queue, targets, READY_QUEUE, TASK_TTL
    )
    log.info("retry_from %s -> %d tasks", selector, count)
    return {"count": count}


@rpc.method("Guard.set")
async def guard_set(label: str, spec: dict) -> dict:
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
async def task_get(taskId: str) -> dict:
    try:
        uuid.UUID(taskId)
    except ValueError:
        raise RPCException(code=-32602, message="Invalid task id")
    if t := await _load_task(taskId):
        data = t.model_dump()
        if t.duration is not None:
            data["duration"] = t.duration
        return data
    try:
        from ..core.task_core import get_task_result

        return await get_task_result(taskId)
    except TaskNotFoundError as exc:
        raise RPCException(code=ErrorCode.TASK_NOT_FOUND, message=str(exc))
