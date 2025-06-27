"""Utilities for task handler modules."""

from __future__ import annotations

from typing import Any, Dict

from peagen.models import Task
from peagen.models.schemas import TaskRead


def ensure_task(task: Task | Dict[str, Any]) -> Task:
    """Return ``task`` as a :class:`~peagen.models.task.Task` instance."""

    if isinstance(task, Task):
        return task
    return TaskRead.model_validate(task)


__all__ = ["ensure_task"]
