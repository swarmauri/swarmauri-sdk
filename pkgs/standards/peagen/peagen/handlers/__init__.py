"""Utilities for task handler modules."""

from __future__ import annotations

from typing import Any, Dict

import uuid
from types import SimpleNamespace

from peagen.models import Task
from peagen.models import schemas


def ensure_task(task: Task | Dict[str, Any]) -> schemas.TaskRead | Task:
    """Return ``task`` as a :class:`~peagen.models.schemas.TaskRead` instance."""

    if isinstance(task, Task):
        return task

    try:
        return schemas.TaskRead.model_validate(task)
    except Exception:
        defaults = {
            "id": str(uuid.uuid4()),
            "pool": "default",
            "payload": {},
        }
        if isinstance(task, dict):
            defaults.update(task)
        return SimpleNamespace(**defaults)


__all__ = ["ensure_task"]
