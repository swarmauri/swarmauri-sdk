"""Utilities for task handler modules."""

from __future__ import annotations

from typing import Any, Dict
import uuid

from peagen.orm import Task
from peagen.schemas import TaskRead


def ensure_task(task: Task | Dict[str, Any]) -> TaskRead | Task:
    """Return ``task`` as a :class:`~peagen.schemas.TaskRead` instance.

    Falls back to constructing a minimal :class:`~peagen.orm.Task` when required fields
    are missing (e.g. during unit tests).
    """

    if isinstance(task, Task):
        return task
    try:
        return TaskRead.model_validate(task)
    except Exception:
        tmp = Task(
            id=str(uuid.uuid4()),
            tenant_id=uuid.uuid4(),
            parameters={},
            note=None,
        )
        tmp.pool = task.get("pool", "default")
        tmp.payload = task.get("payload", {})
        return tmp


__all__ = ["ensure_task"]
