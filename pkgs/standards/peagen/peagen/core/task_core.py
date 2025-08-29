"""Utility helpers for building, submitting and fetching Task rows
from an AutoAPI gateway.
"""

from __future__ import annotations

import httpx
from typing import Any, Dict

from autoapi_client import AutoAPIClient
from autoapi.v3 import get_schema
from peagen.orm import Task

from peagen.defaults import DEFAULT_GATEWAY, RPC_TIMEOUT


# ────────────────────────── internal helpers ───────────────────────── #
def _schema(tag: str):
    """Return the server-generated schema for <Task, tag>."""
    return get_schema(Task, tag)


def _rpc(url: str, *, timeout: float = RPC_TIMEOUT) -> AutoAPIClient:
    return AutoAPIClient(url, client=httpx.Client(timeout=timeout))


# ────────────────────────── public helpers ────────────────────────────


def submit_task(
    gateway_url: str,
    task: Any,
    *,
    timeout: float = RPC_TIMEOUT,
) -> Dict[str, Any]:
    """Submit *task* to *gateway_url* and return the created Task (dict)."""

    SRead = _schema("read")

    with _rpc(gateway_url, timeout=timeout) as rpc:
        res = rpc.call("Tasks.create", params=task, out_schema=SRead)

    return res.model_dump()


def get_task_result(
    task_id: str,
    *,
    gateway_url: str = DEFAULT_GATEWAY,
    timeout: float = RPC_TIMEOUT,
) -> Dict[str, Any]:
    """
    Fetch status / result / metadata for *task_id* via JSON-RPC and return

        {
          "status":         "...",
          "result":         {... or None},
          "oids":           [... or None],
          "commit_hexsha":  "...",
          "date_created":   "2025-06-04T12:34:56Z" | None,
          "last_modified":  "... | None",
          "duration":       seconds | None
        }
    """
    SRead = _schema("read")
    SKey = _schema("delete")  # pk-only schema (id field)

    with _rpc(gateway_url, timeout=timeout) as rpc:
        task = rpc.call("Tasks.read", params=SKey(id=task_id), out_schema=SRead)

    # post-process → match the server-side structure used by earlier helpers
    dc = task.date_created
    lm = task.last_modified
    return {
        "status": task.status,
        "result": task.result,
        "oids": task.oids,
        "commit_hexsha": task.commit_hexsha,
        "date_created": dc.isoformat() if dc else None,
        "last_modified": lm.isoformat() if lm else None,
        "duration": (int((lm - dc).total_seconds()) if dc and lm else None),
    }
