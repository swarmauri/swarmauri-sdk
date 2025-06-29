"""Utilities for task handler modules."""

from __future__ import annotations


import uuid

from peagen.orm.status import Status
from peagen.protocols.methods.task import SubmitParams


def ensure_task(task: SubmitParams) -> SubmitParams:
    """Return ``task`` as a :class:`~peagen.protocols.methods.task.PatchResult` instance."""

    if isinstance(task, SubmitParams):
        return task

    if not isinstance(task, dict):  # pragma: no cover - defensive
        if hasattr(task, "model_dump"):
            task = task.model_dump(mode="json")
        else:
            raise TypeError(f"Expected dict or PatchResult, got {type(task)!r}")

    # If the incoming mapping is missing required fields, assume it comes from
    # a local CLI invocation and populate sane defaults so handler logic can
    # operate on a complete ``PatchResult`` model.
    defaults = {
        "pool": task.get("pool", "default"),
        "payload": task.get("payload", {}),
        "status": Status.queued,
        "note": ""
    }

    merged = {**defaults, **task}
    try:
        return SubmitParams.model_validate(merged)
    except Exception:  # pragma: no cover - fallback for invalid input
        merged["id"] = str(uuid.uuid4())
        return SubmitParams.model_validate(merged)


__all__ = ["ensure_task"]
