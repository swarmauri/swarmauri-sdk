# task_helpers.py  – aligned with Task v3
from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from autoapi_client import AutoAPIClient
from autoapi.v3 import get_schema
from peagen.orm import Status, Task, Action, SpecKind


# ─────────────────── local factory ──────────────────────────────────────
def build_task(
    *,
    pool_id: str,
    action: Action | str,
    repo: str,
    ref: str,
    repository_id: str | None = None,
    args: Dict[str, Any] | None = None,
    # Optional columns
    config_toml: Optional[str] = None,
    spec_kind: Optional[SpecKind | str] = None,
    spec_uuid: Optional[str] = None,
    note: Optional[str] = None,
    labels: Optional[Dict[str, Any]] = None,
    status: Status = Status.WAITING,
):
    """
    Return a TaskCreate Pydantic instance that matches AutoAPI's
    current schema (no 'payload' column any more).
    """
    SCreate = get_schema(Task, "read")

    if not isinstance(action, Action):
        try:
            action = Action[action.upper()]
        except KeyError:
            action = str(action)
    if spec_kind is not None and not isinstance(spec_kind, SpecKind):
        spec_kind = SpecKind(spec_kind)

    return SCreate.model_construct(
        id=uuid.uuid4(),
        pool_id=pool_id,
        action=action,
        repository_id=repository_id,  # may be None → pre-hook resolves it
        repo=repo,
        ref=ref,
        config_toml=config_toml,
        spec_kind=spec_kind,
        spec_uuid=spec_uuid,
        args=args or {},
        labels=labels or {},
        note=note,
        status=status,
    )


# ─────────────────── RPC helpers ────────────────────────────────────────
def submit_task(
    rpc: AutoAPIClient | str,
    task_model: Any,  # instance from build_task()
) -> Dict[str, Any]:
    """POST ``tasks.create`` and return the validated TaskRead dict.

    Parameters
    ----------
    rpc
        Either an :class:`autoapi_client.AutoAPIClient` instance or a string
        representing the gateway URL. When a URL is provided, a temporary
        ``AutoAPIClient`` is created for the duration of the request.
    task_model
        A model produced by :func:`build_task`.
    """

    SRead = get_schema(Task, "read")
    params = task_model.model_dump()  # AutoAPIClient expects dict

    if isinstance(rpc, str):
        with AutoAPIClient(rpc) as client:
            res = client.call("tasks.create", params=params, out_schema=SRead)
    else:
        res = rpc.call("tasks.create", params=params, out_schema=SRead)

    return res.model_dump()


def get_task(
    rpc: AutoAPIClient,
    task_id: str,
):
    """Return a validated TaskRead Pydantic object for *task_id*."""
    SRead = get_schema(Task, "read")
    result = rpc.call(
        "tasks.read",
        params={"id": task_id},
        out_schema=SRead,
    )
    return result
