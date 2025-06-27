"""Utilities for task handler modules."""

from __future__ import annotations

from typing import Any, Dict

from peagen.schemas import TaskRead


def ensure_task(task: TaskRead | Dict[str, Any]) -> TaskRead:
    """Return ``task`` as a :class:`~peagen.schemas.TaskRead` instance."""

    if isinstance(task, TaskRead):
        return task
    return TaskRead.model_validate(task)


__all__ = ["ensure_task"]
