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

    if not isinstance(task, dict):  # pragma: no cover - defensive
        raise TypeError(f"Expected dict or TaskRead, got {type(task)!r}")

    # If the incoming mapping is missing required fields, assume it comes from
    # a local CLI invocation and populate sane defaults so handler logic can
    # operate on a complete ``TaskRead`` model.
    defaults = {
        "id": uuid.uuid4(),
        "tenant_id": uuid.uuid4(),
        "git_reference_id": uuid.uuid4(),
        "pool": task.get("pool", "default"),
        "payload": task.get("payload", {}),
        "status": Status.queued,
        "note": "",
        "spec_hash": uuid.uuid4().hex * 2,
        "date_created": datetime.now(timezone.utc),
        "last_modified": datetime.now(timezone.utc),
    }

    merged = {**defaults, **task}
    return TaskRead.model_validate(merged)


__all__ = ["ensure_task"]
