"""Helpers for building and submitting tasks via the TUI."""

from __future__ import annotations

import httpx
import uuid
from datetime import datetime
from typing import Any

from peagen.schemas import TaskCreate
from peagen.defaults import TASK_SUBMIT
from peagen.orm.status import Status


def build_task(action: str, args: dict[str, Any], pool: str = "default") -> TaskCreate:
    """Construct a :class:`TaskCreate` from CLI-style arguments."""

    task = TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool=pool,
        payload={"action": action, "args": args},
        status=Status.queued,
        note="",
        spec_hash="dummy",
        last_modified=datetime.utcnow(),
    )
    # Expose identifier as string for consistency with CLI-generated tasks
    task.id = str(task.id)
    return task


def submit_task(gateway_url: str, task: TaskCreate) -> dict:
    """Submit *task* to the gateway via JSON-RPC and return the reply."""

    req = {
        "jsonrpc": "2.0",
        "method": TASK_SUBMIT,
        "params": {"taskId": task.id, "pool": task.pool, "payload": task.payload},
    }
    resp = httpx.post(gateway_url, json=req, timeout=30.0)
    resp.raise_for_status()
    return resp.json()
