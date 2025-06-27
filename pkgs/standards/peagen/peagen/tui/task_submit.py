"""Helpers for building and submitting tasks via the TUI."""

from __future__ import annotations

import httpx
from typing import Any

from peagen.models.task import Task


def build_task(action: str, args: dict[str, Any], pool: str = "default") -> Task:
    """Construct a :class:`Task` from CLI-style arguments."""

    return Task(pool=pool, payload={"action": action, "args": args})


def submit_task(gateway_url: str, task: Task) -> dict:
    """Submit *task* to the gateway via JSON-RPC and return the reply."""

    req = {
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {"taskId": task.id, "pool": task.pool, "payload": task.payload},
    }
    resp = httpx.post(gateway_url, json=req, timeout=30.0)
    resp.raise_for_status()
    return resp.json()
