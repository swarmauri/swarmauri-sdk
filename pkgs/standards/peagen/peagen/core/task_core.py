"""
Business-logic for reading a TaskRun row.

Public entry-point
------------------
get_task_result()  – fetch status / result / metadata for a task-id.
"""

from __future__ import annotations
from typing import Dict

from peagen.gateway.db import Session
from peagen.models import TaskRun
from sqlalchemy import select


async def get_task_result(task_id: str, tenant_id: str = "default") -> Dict:
    """
    Return a JSON-serialisable dict:

        {"status": "running|finished|failed",
         "result":        {... or None},
         "artifact_uri":  "... or None",
         "started_at":    "2025-06-04T12:34:56Z" | None,
         "finished_at":   "... | None"}
    """
    async with Session() as s:
        result = await s.execute(
            select(TaskRun).where(TaskRun.id == task_id, TaskRun.tenant_id == tenant_id)
        )
        tr: TaskRun | None = result.scalar_one_or_none()
        if tr is None:
            raise ValueError(f"Task '{task_id}' not found")

        return {
            "status": tr.status,
            "result": tr.result,
            "artifact_uri": tr.artifact_uri,
            "commit_hexsha": tr.commit_hexsha,
            "started_at": tr.started_at.isoformat() if tr.started_at else None,
            "finished_at": tr.finished_at.isoformat() if tr.finished_at else None,
            "duration": (
                int((tr.finished_at - tr.started_at).total_seconds())
                if tr.started_at and tr.finished_at
                else None
            ),
        }
