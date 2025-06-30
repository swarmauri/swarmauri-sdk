"""
Business-logic for reading a TaskRun row.

Public entry-point
------------------
get_task_result()  – fetch status / result / metadata for a task-id.
"""

from __future__ import annotations
from typing import Dict

from peagen.gateway.db import Session
from peagen.orm import TaskRunModel
from sqlalchemy.exc import DataError
from peagen.errors import TaskNotFoundError


async def get_task_result(task_id: str) -> Dict:
    """
    Return a JSON-serialisable dict:

        {"status": "running|finished|failed",
         "result":        {... or None},
         "oids":         [... or None],
         "date_created":  "2025-06-04T12:34:56Z" | None,
         "last_modified": "... | None"}
    """
    async with Session() as s:
        try:
            tr: TaskRunModel | None = await s.get(TaskRunModel, task_id)
        except DataError:
            raise TaskNotFoundError(task_id) from None
        if tr is None:
            raise TaskNotFoundError(task_id)

        return {
            "status": tr.status,
            "result": tr.result,
            "oids": tr.oids,
            "commit_hexsha": tr.commit_hexsha,
            "date_created": tr.date_created.isoformat() if tr.date_created else None,
            "last_modified": tr.last_modified.isoformat() if tr.last_modified else None,
            "duration": (
                int((tr.last_modified - tr.date_created).total_seconds())
                if tr.date_created and tr.last_modified
                else None
            ),
        }
