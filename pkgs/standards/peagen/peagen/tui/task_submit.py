"""Helpers for building and submitting tasks via the TUI."""

from __future__ import annotations

import httpx
import uuid
from typing import Any

from peagen.schemas import TaskCreate
from peagen.protocols import Request as RPCEnvelope, TASK_SUBMIT
from peagen.cli.task_builder import _build_task


def build_task(action: str, args: dict[str, Any], pool: str = "default") -> TaskCreate:
    """Return a :class:`TaskCreate` for *action* using *args*."""

    return _build_task(action, args, pool)


def submit_task(gateway_url: str, task: TaskCreate) -> dict:
    """Submit *task* to the gateway via JSON-RPC and return the reply."""

    req = RPCEnvelope(
        id=str(uuid.uuid4()),
        method=TASK_SUBMIT,
        params=task.model_dump(mode="json"),
    ).model_dump()
    resp = httpx.post(gateway_url, json=req, timeout=30.0)
    resp.raise_for_status()
    return resp.json()
