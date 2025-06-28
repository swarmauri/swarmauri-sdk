from __future__ import annotations

import json
import uuid

from peagen.transport.jsonrpc import RPCException
from peagen.defaults.error_codes import ErrorCode
from peagen.defaults import (
    TASK_SUBMIT,
    TASK_CANCEL,
    TASK_PAUSE,
    TASK_RESUME,
    TASK_RETRY,
    TASK_RETRY_FROM,
    GUARD_SET,
    TASK_PATCH,
    TASK_GET,
)

from .. import (
    READY_QUEUE,
    TASK_TTL,
    _finalize_parent_tasks,
    _live_workers_by_pool,
    _load_task,
    _persist,
    _publish_queue_length,
    _publish_task,
    _save_task,
    _select_tasks,
    dispatcher,
    log,
    queue,
)
from peagen.errors import TaskNotFoundError
from peagen.schemas import TaskCreate, TaskRead, TaskUpdate
from peagen.orm.task.task import TaskModel
from peagen.orm.task.task_run import TaskRunModel
from peagen.orm.status import Status
from sqlalchemy.ext.asyncio import AsyncSession as Session


@dispatcher.method(TASK_SUBMIT)
async def task_submit(dto: TaskCreate) -> dict:
    """Persist *dto* and enqueue the task."""

    await queue.sadd("pools", dto.pool)

    action = (dto.payload or {}).get("action")
    handlers: set[str] = set()
    for w in await _live_workers_by_pool(dto.pool):
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

    task_id = dto.id
    if task_id and await _load_task(task_id):
        new_id = str(uuid.uuid4())
        log.warning("task id collision: %s → %s", task_id, new_id)
        task_id = new_id

    async with Session() as ses:
        # 1. create definition-of-task row
        payload = dto.model_dump()
        if task_id:
            payload["id"] = task_id
        task_db = TaskModel(**payload)
        ses.add(task_db)
        await ses.flush()  # gets task_db.id

        # 2. create first execution attempt
        run_db = TaskRunModel(task_id=task_db.id, status=Status.queued)
        ses.add(run_db)
        await ses.commit()

    # 3. make the object that will travel over Redis / websockets
    task_rd = TaskRead.model_validate(task_db.__dict__)

    await queue.rpush(f"{READY_QUEUE}:{task_rd.pool}", task_rd.model_dump_json())
    await _publish_queue_length(task_rd.pool)
    await _save_task(task_rd)
    await _publish_task(task_rd)
    log.info("task %s queued in %s (ttl=%ss)", task_rd.id, task_rd.pool, TASK_TTL)
    return {"taskId": str(task_rd.id)}


@dispatcher.method(TASK_CANCEL)
async def task_cancel(selector: str) -> dict:
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("cancel", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("cancel %s -> %d tasks", selector, count)
    return {"count": count}


@dispatcher.method(TASK_PAUSE)
async def task_pause(selector: str) -> dict:
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("pause", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("pause %s -> %d tasks", selector, count)
    return {"count": count}


@dispatcher.method(TASK_RESUME)
async def task_resume(selector: str) -> dict:
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("resume", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("resume %s -> %d tasks", selector, count)
    return {"count": count}


@dispatcher.method(TASK_RETRY)
async def task_retry(selector: str) -> dict:
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("retry", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("retry %s -> %d tasks", selector, count)
    return {"count": count}


@dispatcher.method(TASK_RETRY_FROM)
async def task_retry_from(selector: str) -> dict:
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply(
        "retry_from", queue, targets, READY_QUEUE, TASK_TTL
    )
    log.info("retry_from %s -> %d tasks", selector, count)
    return {"count": count}


@dispatcher.method(GUARD_SET)
async def guard_set(label: str, spec: dict) -> dict:
    await queue.hset(f"guard:{label}", mapping=spec)
    log.info("guard set %s", label)
    return {"ok": True}


@dispatcher.method(TASK_PATCH)
async def task_patch(taskId: str, changes: dict) -> dict:
    """Update persisted metadata for an existing task."""
    task = await _load_task(taskId)
    if not task:
        raise TaskNotFoundError(taskId)

    for field, value in changes.items():
        if field not in TaskUpdate.model_fields:
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


@dispatcher.method(TASK_GET)
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
