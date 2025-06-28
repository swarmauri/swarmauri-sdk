"""Utilities for task handler modules."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

import uuid

from peagen.orm.status import Status
from peagen.schemas import TaskRead


def ensure_task(task: TaskRead | Dict[str, Any]) -> TaskRead:
    """Return ``task`` as a :class:`~peagen.schemas.TaskRead` instance."""

    if isinstance(task, TaskRead):
        return task
    if not isinstance(task, dict):
        raise TypeError("task must be a mapping or TaskRead instance")

    try:
        return TaskRead.model_validate(task)
    except Exception:
        now = datetime.now(timezone.utc)
        return TaskRead.model_construct(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            git_reference_id=None,
            pool=task.get("pool", "default"),
            payload=task.get("payload", {}),
            status=task.get("status", Status.queued),
            note=task.get("note"),
            spec_hash=task.get("spec_hash", ""),
            date_created=now,
            last_modified=now,
        )


__all__ = ["ensure_task"]
