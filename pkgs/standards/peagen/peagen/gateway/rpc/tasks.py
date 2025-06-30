from __future__ import annotations

import json
import uuid
from peagen.transport.jsonrpc import RPCException
from peagen.transport.error_codes import ErrorCode

from peagen.transport import (
    TASK_SUBMIT,
    TASK_CANCEL,
    TASK_PAUSE,
    TASK_RESUME,
    TASK_RETRY,
    TASK_RETRY_FROM,
    TASK_PATCH,
    TASK_GET,
)
from peagen.transport.jsonrpc_schemas.task import (
    SubmitParams,
    SubmitResult,
    PatchParams,
    PatchResult,
    SimpleSelectorParams,
    CountResult,
    GetParams,
    GetResult,
)
from peagen.transport.jsonrpc_schemas.guard import GUARD_SET

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
from typing import Any, Dict
from peagen.orm.task.task import TaskModel
from peagen.orm.task.task_run import TaskRunModel
from peagen.transport.jsonrpc_schemas import Status

# Use the Session factory configured by the gateway
from .. import Session, engine, Base

# -----------------TaskBlob ------------------------------------

TaskBlob = Dict[str, Any]  # canonical on-wire / in-Redis structure


# -----------------Helper---------------------------------------


def _normalise_submit_payload(raw: dict) -> TaskBlob:
    """
    Ensure required fields exist and assign sensible defaults.
    This is the only validation performed at the RPC layer.
    """
    blob: TaskBlob = {
        "id": raw.get("id") or uuid.uuid4().hex,
        "tenant_id": raw.get("tenant_id"),
        "git_reference_id": raw.get("git_reference_id"),
        "pool": raw.get("pool", "default"),
        "payload": raw.get("payload", {}),
        "status": raw.get("status", Status.queued),
        "note": raw.get("note", ""),
        "labels": raw.get("labels", []),
        "spec_hash": raw.get("spec_hash", ""),
        "last_modified": raw.get("last_modified"),
    }
    return blob


# --------------Basic Task Methods ---------------------------------


@dispatcher.method(TASK_SUBMIT)
async def task_submit(params: SubmitParams) -> SubmitResult:
    """
    Persist the task definition, enqueue it, and notify listeners.
    Uses TaskModel + TaskRunModel for Postgres; everywhere else passes TaskBlob.
    """
    # 1. Build the raw blob -----------------------------------------
    raw_task = getattr(params, "task", None)
    if raw_task is not None:
        task_blob = _normalise_submit_payload(dict(raw_task))
    else:
        extra = getattr(params, "__pydantic_extra__", {}) or {}
        base = {
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
        task_blob = _normalise_submit_payload(base)

    await queue.sadd("pools", task_blob["pool"])

    # 2. Verify a worker exists for the requested action ------------
    action = (task_blob["payload"] or {}).get("action")
    if action:
        available = {
            h
            for w in await _live_workers_by_pool(task_blob["pool"])
            for h in (
                json.loads(w.get("handlers", "[]"))
                if isinstance(w.get("handlers"), str)
                else w.get("handlers", [])
            )
        }
        if action not in available:
            log.warning("no worker advertising '%s' found", action)

    # 3. Avoid id collision in Redis --------------------------------
    if await _load_task(task_blob["id"]):
        task_blob["id"] = uuid.uuid4().hex
        log.warning("task id collision – generated new id %s", task_blob["id"])

    # 4. Persist to Postgres (skip if id is not a UUID) -------------
    try:
        uuid.UUID(task_blob["id"])
        persist = True
    except ValueError:
        persist = False
    if task_blob.get("tenant_id") is None:
        persist = False

    if persist:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with Session() as ses:
            orm_fields = {
                k: task_blob[k]
                for k in _ORM_COLUMNS
                if k in task_blob and task_blob[k] is not None
            }
            for col in ("id", "tenant_id", "git_reference_id"):
                if col in orm_fields and isinstance(orm_fields[col], str):
                    try:
                        orm_fields[col] = uuid.UUID(str(orm_fields[col]))
                    except ValueError:
                        pass
            model = TaskModel(**orm_fields)
            ses.merge(model)  # insert or update
            ses.add(TaskRunModel(task_id=model.id, status=Status.queued))
            await ses.commit()

    # 5. Push onto ready queue & broadcast --------------------------
    await queue.rpush(
        f"{READY_QUEUE}:{task_blob['pool']}", json.dumps(task_blob, default=str)
    )
    await _publish_queue_length(task_blob["pool"])
    await _save_task(task_blob)
    await _publish_task(task_blob)

    log.info(
        "task %s queued in %s (ttl=%ss)", task_blob["id"], task_blob["pool"], TASK_TTL
    )

    # ``SubmitResult`` expects an ``id`` field. Returning ``taskId`` results in
    # a validation error with ``extra_forbidden``. Use the canonical field name
    # to ensure callers receive a valid model instance.
    return SubmitResult(id=str(task_blob["id"]))


# ------------------------------------------------------------------
# PATCH  ▸  update in-cache blob  ▸  persist  ▸  broadcast
# ------------------------------------------------------------------

# helper: canonical field set that can be patched
_ORM_COLUMNS = {c.name for c in TaskModel.__table__.columns}
_ALLOWED_PATCH_EXTRAS = {"labels", "result"}


@dispatcher.method(TASK_PATCH)
async def task_patch(params: PatchParams) -> PatchResult:
    task_id = params.taskId
    changes = params.changes

    task = await _load_task(task_id)  # TaskBlob | None
    if not task:
        raise TaskNotFoundError(task_id)

    for field, value in changes.items():
        # skip unknown columns
        if field not in _ORM_COLUMNS and field not in _ALLOWED_PATCH_EXTRAS:
            continue
        # coerce status enum
        if field == "status":
            value = Status(value)
        task[field] = value  # apply in-memory

    await _save_task(task)  # Redis cache
    await _persist(task)  # Postgres + result backend
    await _publish_task(task)  # WebSocket event

    # cascade completion checks for parent tasks, if needed
    if isinstance(changes.get("result"), dict):
        for cid in changes["result"].get("children", []):
            await _finalize_parent_tasks(cid)

    log.info("task %s patched with %s", task_id, ",".join(changes.keys()))

    # Return only fields declared by PatchResult schema
    filtered = {k: v for k, v in task.items() if k in PatchResult.model_fields}
    return PatchResult(**filtered)


# ------------------------------------------------------------------
# GET  ▸  fetch from cache or DB fall-back
# ------------------------------------------------------------------
@dispatcher.method(TASK_GET)
async def task_get(params: GetParams) -> GetResult | dict:
    task_id = params.taskId

    # quick sanity check – client ought to supply a UUID-ish id
    try:
        uuid.UUID(task_id)
    except ValueError:
        raise RPCException(code=-32602, message="Invalid task id")

    task = await _load_task(task_id)
    if task:
        # optional duration passthrough
        data = dict(task)
        if "duration" in task and task["duration"] is not None:
            data["duration"] = task["duration"]
        filtered = {k: v for k, v in data.items() if k in GetResult.model_fields}
        return GetResult(**filtered)

    # fall-back to slower path (possibly worker-side DB)
    try:
        from ..core.task_core import get_task_result

        return await get_task_result(task_id)
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
