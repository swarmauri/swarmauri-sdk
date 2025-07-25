"""
gateway.api.hooks.works
───────────────────────
Propagate terminal Work status/result to the cached Task object.
Everything is expressed with AutoAPI-generated Pydantic schemas.
"""

from __future__ import annotations

from typing import Any, Dict

from autoapi.v2 import AutoAPI, Phase

from peagen.orm import Status, Task, Work

from peagen.gateway import api, log, queue
from peagen.gateway._publish import _publish_task
from peagen.gateway.schedule_helpers import (
    _finalize_parent_tasks,
    _load_task,
    _save_task,
)

# ─────────────────── schema handles ────────────────────────────────────
WorkRead = AutoAPI.get_schema(Work, "read")
WorkUpdate = AutoAPI.get_schema(Work, "update")
TaskRead = AutoAPI.get_schema(Task, "read")


# ─────────────────── POST-COMMIT hook for Work.update ─────────────────
@api.hook(Phase.POST_COMMIT, model="Work", op="update")
async def post_work_update(ctx: Dict[str, Any]) -> None:
    """
    When a Work row becomes terminal, update the cached Task and fan-out.
    """
    log.info("entering post_work_update")

    wr: WorkRead = ctx["result"]

    # only act on terminal statuses
    if not Status.is_terminal(wr.status):
        return

    task = await _load_task(queue, str(wr.task_id))
    if task is None:
        log.warning("terminal Work for unknown Task %s", wr.task_id)
        return

    # mutate a copy of the TaskRead model
    updated = task.model_copy(
        update={
            "status": wr.status,
            "result": wr.result or {},
            "last_modified": wr.last_modified,
        }
    )

    await _save_task(queue, updated)
    await _publish_task(updated.model_dump(mode="json"))
    await _finalize_parent_tasks(str(wr.task_id))

    log.info("Task %s closed via Work %s → %s", wr.task_id, wr.id, wr.status)
