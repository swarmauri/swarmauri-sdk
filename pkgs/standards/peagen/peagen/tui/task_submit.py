"""Helpers for building and submitting tasks via the TUI."""

from __future__ import annotations

import httpx
from typing import Any

import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

from peagen.schemas import TaskCreate
from peagen.defaults import TASK_SUBMIT


def _spec_hash(obj: dict[str, Any]) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()


def build_task(action: str, args: dict[str, Any], pool: str = "default") -> TaskCreate:
    """Construct a :class:`TaskCreate` from CLI-style arguments."""

    payload = {"action": action, "args": args, "pool": pool}
    return TaskCreate(
        id=uuid4(),
        tenant_id=uuid4(),
        git_reference_id=uuid4(),
        parameters=payload,
        note="",
        spec_hash=_spec_hash(payload),
        last_modified=datetime.now(timezone.utc),
    )


def submit_task(gateway_url: str, task: TaskCreate) -> dict:
    """Submit *task* to the gateway via JSON-RPC and return the reply."""

    req = {
        "jsonrpc": "2.0",
        "method": TASK_SUBMIT,
        "params": json.loads(task.model_dump_json()),
    }
    resp = httpx.post(gateway_url, json=req, timeout=30.0)
    resp.raise_for_status()
    return resp.json()
