"""Utilities for task handler modules."""

from __future__ import annotations

from typing import Any, Dict

from peagen.models import Task
from peagen.schemas import TaskRead


def ensure_task(task: Task | Dict[str, Any]) -> TaskRead | Task:
    """Return ``task`` as a :class:`~peagen.schemas.TaskRead` instance."""

    if isinstance(task, Task):
        return task
    return TaskRead.model_validate(task)


__all__ = ["ensure_task"]
