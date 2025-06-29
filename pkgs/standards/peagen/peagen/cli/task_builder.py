from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from peagen.orm.status import Status
from peagen.protocols.methods.task import SubmitParams


def _build_task(
    action: str,
    args: dict[str, Any],
    pool: str = "default",
    *,
    status: Status = Status.queued,
) -> Any:
    """Return a Task model (via :class:`SubmitParams`) with *action* and *args* embedded."""

    submit = SubmitParams(
        task={
            "id": uuid.uuid4(),
            "tenant_id": uuid.uuid4(),
            "git_reference_id": uuid.uuid4(),
            "pool": pool,
            "payload": {"action": action, "args": args},
            "status": status,
            "note": "",
            "spec_hash": "dummy",
            "last_modified": datetime.utcnow(),
        }
    )
    task = submit.task
    task.id = str(task.id)
    return task


def build_submit_params(
    action: str,
    args: dict[str, Any],
    pool: str = "default",
    *,
    status: Status = Status.queued,
) -> SubmitParams:
    """Return :class:`SubmitParams` with defaults populated."""

    task = _build_task(action, args, pool, status=status)
    return SubmitParams(task=task)
