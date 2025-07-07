"""
peagen.handlers.control_handler
────────────────────────────────
Pause / resume / cancel / retry helpers that operate on the
AutoAPI-generated **TaskUpdate** model.

All callers must pass an *iterable* of TaskUpdate instances.
"""

from __future__ import annotations

from typing import Iterable

from autoapi          import AutoAPI
from autoapi.v2.tables.task import Task               # SQLAlchemy row

from peagen.core            import control_core
from peagen.plugins.queues  import QueueBase
from peagen                  import defaults

# ────────────────────────── AutoAPI schemas ───────────────────────────
TaskUpdate = AutoAPI.get_schema(Task, "update")       # ← concrete type

TASK_KEY = defaults.CONFIG["task_key"]


async def _save_task_redis(queue: QueueBase, t: TaskUpdate, ttl: int) -> None:
    """
    Persist *t* (TaskUpdate) in Redis under task:<id>.
    Hash fields:
        • blob   – canonical JSON string
        • status – enum value (str)
    """
    await queue.hset(
        TASK_KEY.format(t.id),
        mapping={
            "blob":   t.model_dump_json(),
            "status": str(t.status.value if hasattr(t.status, "value") else t.status),
        },
    )
    await queue.expire(TASK_KEY.format(t.id), ttl)


async def apply(                        # noqa: C901 complexity unchanged
    op: str,
    queue: QueueBase,
    tasks: Iterable[TaskUpdate],
    ready_prefix: str,
    ttl: int,
) -> int:
    """
    Apply *op* (“pause”, “resume”, “cancel”, “retry”, “retry_from”)
    to each TaskUpdate in *tasks*, update Redis, and (for retry ops)
    re-queue the task JSON onto <ready_prefix>:<pool>.

    Returns the number of tasks affected.
    """
    if op == "pause":
        count = control_core.pause(tasks)
    elif op == "resume":
        count = control_core.resume(tasks)
    elif op == "cancel":
        count = control_core.cancel(tasks)
    elif op == "retry_from":
        count = control_core.retry_from(tasks)
    elif op == "retry":
        count = control_core.retry(tasks)
    else:
        return 0

    for t in tasks:
        # 1️⃣  persist updated state
        await _save_task_redis(queue, t, ttl)

        # 2️⃣  re-queue retried tasks
        if op in {"retry", "retry_from"}:
            await queue.rpush(f"{ready_prefix}:{t.pool}", t.model_dump_json())

    return count
