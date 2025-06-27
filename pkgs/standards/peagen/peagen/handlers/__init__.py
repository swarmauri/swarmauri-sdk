"""Utilities for task handler modules."""

from __future__ import annotations

from typing import Any, Dict

from peagen.schemas import TaskRead


def ensure_task(task: TaskRead) -> Task:
    """Return ``task`` as a :class:`~peagen.orm.Task` instance."""

    return TaskRead.model_validate(task)


__all__ = ["ensure_task"]
