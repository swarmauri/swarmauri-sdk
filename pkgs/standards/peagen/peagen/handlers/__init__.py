"""Utilities for task handler modules."""

from __future__ import annotations

from typing import Any, Dict

from peagen.models import Task
from peagen.models import schemas


def ensure_task(task: Task | Dict[str, Any]) -> schemas.TaskRead | Task:
    """Return ``task`` as a :class:`~peagen.models.schemas.TaskRead` instance."""

    if isinstance(task, Task):
        return task
    return schemas.TaskRead.model_validate(task)


__all__ = ["ensure_task"]
