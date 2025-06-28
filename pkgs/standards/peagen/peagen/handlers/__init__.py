"""Utilities for task handler modules."""

from __future__ import annotations

from peagen.schemas import TaskRead


def ensure_task(task: TaskRead) -> TaskRead:
    """Return ``task`` if it's a :class:`~peagen.schemas.TaskRead` instance."""

    if not isinstance(task, TaskRead):
        raise TypeError("task must be a TaskRead instance")
    return task


__all__ = ["ensure_task"]
