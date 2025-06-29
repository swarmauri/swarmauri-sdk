"""Utilities for task handler modules."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
import uuid

from peagen.orm.status import Status
from peagen.protocols.methods.task import PatchResult


def ensure_task(task: PatchResult | Dict[str, Any]) -> PatchResult:
    """Return ``task`` as a :class:`~peagen.protocols.methods.task.PatchResult` instance."""

    if isinstance(task, PatchResult):
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
        "id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "git_reference_id": str(uuid.uuid4()),
        "pool": task.get("pool", "default"),
        "payload": task.get("payload", {}),
        "status": Status.queued,
        "note": "",
        "spec_hash": uuid.uuid4().hex * 2,
        "date_created": datetime.now(timezone.utc).isoformat(),
        "last_modified": datetime.now(timezone.utc).isoformat(),
    }

    merged = {**defaults, **task}
    try:
        return PatchResult.model_validate(merged)
    except Exception:  # pragma: no cover - fallback for invalid input
        merged["id"] = str(uuid.uuid4())
        return PatchResult.model_validate(merged)


__all__ = ["ensure_task"]
