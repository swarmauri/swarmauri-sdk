"""
Business-logic for reading a TaskRun row.

Public entry-point
------------------
get_task_result()  – fetch status / result / metadata for a task-id.
"""

from __future__ import annotations
from typing import Dict

from peagen.gateway.db import Session
from peagen.models.task.task_run import TaskRun
from sqlalchemy.exc import DataError
from peagen.errors import TaskNotFoundError


async def get_task_result(task_id: str) -> Dict:
    """
    Return a JSON-serialisable dict:

        {"status": "running|finished|failed",
         "result":        {... or None},
         "oids":         [... or None],
         "started_at":    "2025-06-04T12:34:56Z" | None,
         "finished_at":   "... | None"}
    """
    async with Session() as s:
        try:
            tr: TaskRun | None = await s.get(TaskRun, task_id)
        except DataError:
            raise TaskNotFoundError(task_id) from None
        if tr is None:
            raise TaskNotFoundError(task_id)

        return {
            "status": tr.status,
            "result": tr.result,
            "oids": tr.oids,
            "commit_hexsha": tr.commit_hexsha,
            "started_at": tr.started_at.isoformat() if tr.started_at else None,
            "finished_at": tr.finished_at.isoformat() if tr.finished_at else None,
            "duration": (
                int((tr.finished_at - tr.started_at).total_seconds())
                if tr.started_at and tr.finished_at
                else None
            ),
        }
