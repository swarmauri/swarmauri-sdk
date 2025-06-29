from __future__ import annotations

import httpx

from peagen.cli.task_builder import build_task
from peagen.transport.envelope import Request
from peagen.transport.jsonrpc_schemas.task import SubmitParams, SubmitResult


def submit_task(url: str, task: Request[SubmitParams]) -> SubmitResult:
    """Send *task* to *url* and return the decoded JSON response."""
    resp = httpx.post(url, json=task.model_dump(mode="json"), timeout=30.0)
    resp.raise_for_status()
    return SubmitResult.model_validate_json(resp.json())

__all__ = ["build_task", "submit_task"]