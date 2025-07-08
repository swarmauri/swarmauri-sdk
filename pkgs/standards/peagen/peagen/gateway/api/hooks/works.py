# gateway/api/hooks/work.py
from __future__ import annotations
from typing import Dict, Any
from autoapi.v2 import Phase, AutoAPI
from peagen.orm import Status, Work, Task

from .. import queue, log, api
from .task import _load_task, _save_task, _finalize_parent_tasks
from .._publish import _publish_task

WorkUpdate = AutoAPI.get_schema(Work, "update")
WorkRead   = AutoAPI.get_schema(Work, "read")

@api.hook(Phase.POST_COMMIT, method="Works.update")
async def post_work_update(ctx: Dict[str, Any]) -> None:
    """
    After a Work row is updated (by a worker), propagate the new status/result
    to the cached Task and observers.
    """
    wr: WorkRead = ctx["result"]
    if not Status.is_terminal(wr.status):
        return                                          # nothing to cascade yet

    task = await _load_task(wr.task_id)
    if not task:
        log.warning("terminal Work for unknown Task %s", wr.task_id)
        return

    # reflect terminal status/result on the Task cache
    task["status"] = wr.status
    task["result"] = wr.result or {}
    task["last_modified"] = ctx["result"].last_modified

    await _save_task(task)
    await _publish_task(task)
    #await _persist(task)
    await _finalize_parent_tasks(wr.task_id)

    log.info("Task %s closed via Work %s → %s", wr.task_id, wr.id, wr.status)
