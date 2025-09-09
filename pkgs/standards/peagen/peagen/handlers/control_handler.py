"""
peagen.handlers.control_handler
────────────────────────────────
Pause / resume / cancel / retry helpers that operate on Tigrbl-generated
**TaskUpdate** objects.

Key changes
-----------
* Uses the canonical helper
    ``peagen.gateway.schedule_helpers._save_task``
  instead of a re-implemented Redis persistence layer.
* No other functional changes.
"""

from __future__ import annotations

from typing import Iterable

from tigrbl.v3 import get_schema
from tigrbl.v3.orm.tables.task import Task  # SQLAlchemy model row

from peagen.core import control_core
from peagen.plugins.queues import QueueBase
from peagen.gateway.schedule_helpers import _save_task  # ← single source of truth

# ─────────────────────────── schemas ────────────────────────────────
TaskUpdate = get_schema(Task, "update")  # validated Pydantic model


# ─────────────────────────── entry-point ────────────────────────────
async def apply(  # noqa: C901 (complex orchestration)
    op: str,
    queue: QueueBase,
    tasks: Iterable[TaskUpdate],
    ready_prefix: str,
    ttl: int,
) -> int:
    """
    Apply *op* (“pause”, “resume”, “cancel”, “retry”, “retry_from”)
    to each TaskUpdate in *tasks*, persist the new state via `_save_task`,
    and (for retry ops) enqueue the task JSON onto ``<ready_prefix>:<pool>``.

    Returns
    -------
    int – number of tasks affected.
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
        return 0  # unknown op

    for t in tasks:
        # 1️⃣  persist updated state (Redis hash + expiry handled by helper)
        await _save_task(queue, t, ttl)

        # 2️⃣  re-queue retried tasks
        if op in {"retry", "retry_from"}:
            await queue.rpush(f"{ready_prefix}:{t.pool}", t.model_dump_json())

    return count
