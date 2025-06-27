"""Utilities for task handler modules."""

from __future__ import annotations

from typing import Any, Dict

from peagen.orm import Task


def ensure_task(task: Task | Dict[str, Any]) -> Task:
    """Return ``task`` as a :class:`~peagen.orm.Task` instance."""

    if isinstance(task, Task):
        return task
    return Task.model_validate(task)


__all__ = ["ensure_task"]
