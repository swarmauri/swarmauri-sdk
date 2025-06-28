"""Helpers for building and submitting tasks via the TUI."""

from __future__ import annotations

import httpx
from typing import Any
from pydantic import TypeAdapter

from peagen.schemas import TaskCreate
from peagen.protocols import Request, Response, TASK_SUBMIT
from peagen.protocols.methods.task import SubmitParams, SubmitResult
from peagen.cli.task_builder import _build_task


def build_task(action: str, args: dict[str, Any], pool: str = "default") -> TaskCreate:
    """Return a :class:`TaskCreate` for *action* using *args*."""

    return _build_task(action, args, pool)


def submit_task(gateway_url: str, task: TaskCreate) -> dict:
    """Submit *task* to the gateway via JSON-RPC and return the reply."""

    params = SubmitParams(task=task).model_dump()
    req = Request(id="1", method=TASK_SUBMIT, params=params).model_dump()
    resp = httpx.post(gateway_url, json=req, timeout=30.0)
    resp.raise_for_status()
    adapter = TypeAdapter(Response[SubmitResult])  # type: ignore[index]
    return adapter.validate_python(resp.json()).model_dump()
