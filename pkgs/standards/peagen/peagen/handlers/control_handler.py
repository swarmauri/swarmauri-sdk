"""Gateway helper for pause/resume/cancel/retry commands."""

from __future__ import annotations

from typing import Iterable

from peagen.plugins.queues import QueueBase
from peagen.transport.jsonrpc_schemas.task import PatchResult, SubmitResult
from peagen.core import control_core
from peagen import defaults


TASK_KEY = defaults.CONFIG["task_key"]


async def save_task(queue: QueueBase, task: SubmitResult, ttl: int) -> None:
    await queue.hset(
        TASK_KEY.format(task.id),
        mapping={"blob": task.model_dump_json(), "status": task.status.value},
    )
    await queue.expire(TASK_KEY.format(task.id), ttl)


async def apply(
    op: str,
    queue: QueueBase,
    tasks: Iterable[PatchResult],
    ready_prefix: str,
    ttl: int,
) -> int:
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
        await save_task(queue, t, ttl)
        if op in {"retry", "retry_from"}:
            await queue.rpush(f"{ready_prefix}:{t.pool}", t.model_dump_json())
    return count
