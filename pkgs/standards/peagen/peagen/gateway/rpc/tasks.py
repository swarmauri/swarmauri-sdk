from __future__ import annotations

import json
import uuid
import typing as t
from peagen.transport.jsonrpc import RPCException
from peagen.protocols.error_codes import Code as ErrorCode

from peagen.protocols import (
    TASK_SUBMIT,
    TASK_CANCEL,
    TASK_PAUSE,
    TASK_RESUME,
    TASK_RETRY,
    TASK_RETRY_FROM,
    TASK_PATCH,
    TASK_GET,
)
from peagen.protocols.methods.task import (
    SubmitParams,
    SubmitResult,
    PatchParams,
    PatchResult,
    SimpleSelectorParams,
    CountResult,
    GetParams,
    GetResult,
)
from peagen.protocols.methods.guard import GUARD_SET

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
from peagen.orm.schemas import TaskCreate, TaskUpdate, TaskRead
from peagen.services.tasks import _to_schema
from peagen.orm.task.task import TaskModel
from peagen.orm.task.task_run import TaskRunModel
from peagen.orm.status import Status

# Use the Session factory configured by the gateway
from .. import Session, engine, Base


# -----------------Helper---------------------------------------


def _parse_task_create(task: t.Any) -> TaskCreate:
    """Return ``task`` if it is a :class:`TaskCreate` instance."""

    if isinstance(task, TaskCreate):
        return task
    if isinstance(task, dict):
        return TaskCreate.model_validate(task)
    raise TypeError("TaskCreate required")


# --------------Basic Task Methods ---------------------------------


@dispatcher.method(TASK_SUBMIT)
async def task_submit(params: SubmitParams) -> SubmitResult:
    """Persist *task* and enqueue it."""
    task_data = getattr(params, "task", None)
    if task_data is None:
        extra = getattr(params, "__pydantic_extra__", {}) or {}
        task_data = {
            "id": extra.get("id"),
            "tenant_id": extra.get("tenant_id"),
            "git_reference_id": extra.get("git_reference_id"),
            "pool": params.pool,
            "payload": params.payload,
            "status": params.status,
            "note": params.note or "",
            "spec_hash": extra.get("spec_hash", ""),
            "last_modified": extra.get("last_modified"),
        }
    dto = _parse_task_create(task_data)
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

    # Determine whether the provided task ID is a valid UUID. If not, we
    # still accept it for in-memory tracking but skip persistence to the
    # relational database to avoid driver errors.
    persist_to_db = True
    if task_id is not None:
        try:
            uuid.UUID(str(task_id))
        except ValueError:
            persist_to_db = False

    task_rd: TaskRead | None = None
    if persist_to_db:
        # Ensure the database schema exists for test environments that
        # do not run migrations.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with Session() as ses:
            # 1. create definition-of-task row
            payload = dto.model_dump()
            if task_id:
                payload["id"] = uuid.UUID(str(task_id))
            task_db = TaskModel(**payload)
            ses.add(task_db)
            await ses.flush()  # gets task_db.id

            # 2. create first execution attempt
            run_db = TaskRunModel(task_id=task_db.id, status=Status.queued)
            ses.add(run_db)
            await ses.commit()

        # 3. make the object that will travel over Redis / websockets
        task_rd = _to_schema(task_db)
    else:
        # Build a ``TaskRead`` instance directly from the provided data without
        # validation to accommodate non-UUID identifiers used in older tests.
        data = dto.model_dump()
        if task_id:
            data["id"] = task_id
        task_rd = TaskRead.model_construct(**data)

    await queue.rpush(f"{READY_QUEUE}:{task_rd.pool}", task_rd.model_dump_json())
    await _publish_queue_length(task_rd.pool)
    await _save_task(task_rd)
    await _publish_task(task_rd)
    log.info("task %s queued in %s (ttl=%ss)", task_rd.id, task_rd.pool, TASK_TTL)
    return SubmitResult(taskId=str(task_rd.id))


@dispatcher.method(TASK_PATCH)
async def task_patch(params: PatchParams) -> PatchResult:
    """Update persisted metadata for an existing task."""
    taskId = params.taskId
    changes = params.changes
    task = await _load_task(taskId)
    if not task:
        raise TaskNotFoundError(taskId)

    for field, value in changes.items():
        if field not in TaskUpdate.model_fields and field not in {"labels", "result"}:
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
    return PatchResult(**task.model_dump(mode="json"))


@dispatcher.method(TASK_GET)
async def task_get(params: GetParams) -> GetResult | dict:
    taskId = params.taskId
    try:
        uuid.UUID(taskId)
    except ValueError:
        raise RPCException(code=-32602, message="Invalid task id")
    if t := await _load_task(taskId):
        data = t.model_dump(mode="json")
        duration = getattr(t, "duration", None)
        if duration is not None:
            data["duration"] = duration
        filtered = {k: v for k, v in data.items() if k in GetResult.model_fields}
        return GetResult(**filtered)
    try:
        from ..core.task_core import get_task_result

        return await get_task_result(taskId)
    except TaskNotFoundError as exc:
        raise RPCException(code=ErrorCode.TASK_NOT_FOUND, message=str(exc))


# ----------- Extended Task Methods --------------------------------


@dispatcher.method(TASK_CANCEL)
async def task_cancel(params: SimpleSelectorParams) -> CountResult:
    selector = params.selector
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("cancel", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("cancel %s -> %d tasks", selector, count)
    return CountResult(count=count)


@dispatcher.method(TASK_PAUSE)
async def task_pause(params: SimpleSelectorParams) -> CountResult:
    selector = params.selector
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("pause", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("pause %s -> %d tasks", selector, count)
    return CountResult(count=count)


@dispatcher.method(TASK_RESUME)
async def task_resume(params: SimpleSelectorParams) -> CountResult:
    selector = params.selector
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("resume", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("resume %s -> %d tasks", selector, count)
    return CountResult(count=count)


@dispatcher.method(TASK_RETRY)
async def task_retry(params: SimpleSelectorParams) -> CountResult:
    selector = params.selector
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply("retry", queue, targets, READY_QUEUE, TASK_TTL)
    log.info("retry %s -> %d tasks", selector, count)
    return CountResult(count=count)


@dispatcher.method(TASK_RETRY_FROM)
async def task_retry_from(params: SimpleSelectorParams) -> CountResult:
    selector = params.selector
    targets = await _select_tasks(selector)
    from peagen.handlers import control_handler

    count = await control_handler.apply(
        "retry_from", queue, targets, READY_QUEUE, TASK_TTL
    )
    log.info("retry_from %s -> %d tasks", selector, count)
    return CountResult(count=count)


# --------Guard Rail Support --------------------------------------


@dispatcher.method(GUARD_SET)
async def guard_set(label: str, spec: dict) -> dict:
    await queue.hset(f"guard:{label}", mapping=spec)
    log.info("guard set %s", label)
    return {"ok": True}
