from __future__ import annotations

import httpx
import uuid

from typing import Optional, List

from peagen.cli.task_builder import build_task
from peagen.transport.envelope import Request
from peagen.transport.jsonrpc_schemas.task import SubmitParams, SubmitResult
from peagen.transport.jsonrpc_schemas import TASK_SUBMIT, Status



def build_task(
    action: str,
    args: dict,
    pool: str = "default",
    *,
    status: Status = Status.queued,
    repo: str | None = None,
    ref: str | None = None,
    note: str | None = None,
    labels: List[str] | None = None,
    config_toml: str | None = None,
    task_id: str | None = None,
) -> Request[SubmitParams]:
    """Return a JSON-RPC request envelope for ``Task.submit``."""
    submit = SubmitParams(
        id=task_id or uuid.uuid4().hex,
        pool=pool,
        repo=repo,
        ref=ref,
        payload={"action": action, "args": args},
        status=status,
        note=note,
        labels=labels,
        config_toml=config_toml,
    )
    return Request(id=submit.id, method=TASK_SUBMIT, params=submit)



def submit_task(url: str, task: Request[SubmitParams]) -> SubmitResult:
    """Send *task* to *url* and return the decoded JSON response."""
    resp = httpx.post(url, json=task.model_dump(mode="json"), timeout=30.0)
    resp.raise_for_status()
    return SubmitResult.model_validate_json(resp.json())

__all__ = ["build_task", "submit_task"]