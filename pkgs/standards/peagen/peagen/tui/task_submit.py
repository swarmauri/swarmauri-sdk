"""Helpers for building and submitting tasks via the TUI."""

from __future__ import annotations

import httpx
from typing import Any

import uuid
from pydantic import BaseModel, Field
from peagen.defaults import TASK_SUBMIT


class SubmitTask(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    pool: str
    payload: dict[str, Any]


def build_task(action: str, args: dict[str, Any], pool: str = "default") -> SubmitTask:
    """Construct a task payload for submission."""

    return SubmitTask(pool=pool, payload={"action": action, "args": args})


def submit_task(gateway_url: str, task: SubmitTask) -> dict:
    """Submit *task* to the gateway via JSON-RPC and return the reply."""

    req = {
        "jsonrpc": "2.0",
        "method": TASK_SUBMIT,
        "params": {"taskId": task.id, "pool": task.pool, "payload": task.payload},
    }
    resp = httpx.post(gateway_url, json=req, timeout=30.0)
    resp.raise_for_status()
    return resp.json()
