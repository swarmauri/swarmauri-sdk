# task_helpers.py  – aligned with Task v3
from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from autoapi_client import AutoAPIClient
from autoapi.v2 import AutoAPI
from peagen.orm import Status, Task, Action, SpecKind


# ─────────────────── local factory ──────────────────────────────────────
def build_task(
    *,
    tenant_id: str,
    pool_id: str,
    action: Action | str,
    repo: str,
    ref: str,
    args: Dict[str, Any] | None = None,
    # Optional columns
    owner_id: Optional[str] = None,
    repository_id: Optional[str] = None,  # slug-only flow leaves this None
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
    SCreate = AutoAPI.get_schema(Task, "create")

    return SCreate(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        pool_id=pool_id,
        action=action,
        owner_id=owner_id,
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
    rpc: AutoAPIClient,
    task_model: Any,  # instance from build_task()
) -> Dict[str, Any]:
    """POST ``tasks.create`` and return the validated TaskRead dict."""
    SRead = AutoAPI.get_schema(Task, "read")
    res = rpc.call(
        "tasks.create",
        params=task_model.model_dump(),  # AutoAPIClient expects dict
        out_schema=SRead,
    )
    return res.model_dump()


def get_task(
    rpc: AutoAPIClient,
    task_id: str,
):
    """Return a validated TaskRead Pydantic object for *task_id*."""
    SRead = AutoAPI.get_schema(Task, "read")
    result = rpc.call(
        "tasks.read",
        params={"id": task_id},
        out_schema=SRead,
    )
    return result
