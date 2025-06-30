from __future__ import annotations

import uuid
from typing import Any, Dict

import httpx

from peagen.defaults import RPC_TIMEOUT
from peagen.transport import Request, Response, TASK_GET
from peagen.transport.jsonrpc_schemas import TASK_SUBMIT, Status
from peagen.transport.jsonrpc_schemas.task import GetParams, GetResult, SubmitParams
from pydantic import BaseModel


class TaskInfo(BaseModel):
    """Minimal task information returned by :func:`get_task`."""

    id: str
    status: Status = Status.running
    result: dict | None = None


def build_task(
    action: str,
    args: Dict[str, Any],
    *,
    pool: str = "default",
    repo: str | None = None,
    ref: str | None = None,
    status: Status = Status.waiting,
    note: str | None = None,
    config_toml: str | None = None,
    labels: list[str] | None = None,
) -> SubmitParams:
    """Return a :class:`SubmitParams` instance for *action* and *args*."""

    return SubmitParams(
        id=str(uuid.uuid4()),
        pool=pool,
        repo=repo,
        ref=ref,
        payload={"action": action, "args": args},
        status=status,
        note=note,
        config_toml=config_toml,
        labels=labels,
    )


def submit_task(gateway_url: str, task: SubmitParams, *, timeout: float = 30.0) -> dict:
    """Submit *task* to *gateway_url* via JSON-RPC and return the response dictionary."""

    envelope = Request(
        id=str(uuid.uuid4()), method=TASK_SUBMIT, params=task.model_dump()
    )
    resp = httpx.post(
        gateway_url, json=envelope.model_dump(mode="json"), timeout=timeout
    )
    resp.raise_for_status()
    return resp.json()


def get_task(
    gateway_url: str,
    task_id: str,
    *,
    timeout: float = RPC_TIMEOUT,
) -> GetResult:
    """Return task information from *gateway_url* via JSON-RPC."""

    envelope = Request(
        id=str(uuid.uuid4()),
        method=TASK_GET,
        params=GetParams(taskId=task_id).model_dump(),
    )
    resp = httpx.post(
        gateway_url, json=envelope.model_dump(mode="json"), timeout=timeout
    )
    resp.raise_for_status()
    data = resp.json()
    result = data.get("result") or {}

    # When talking to a gateway that only returns ``id`` and ``result`` fields,
    # ``status`` may be absent.  Default to ``running`` so callers can still
    # poll until a terminal state is reached.
    if isinstance(result, dict):
        status_val = result.get("status")
        if status_val is None:
            status_val = (
                Status.success if result.get("result") is not None else Status.running
            )
        return TaskInfo(
            id=str(result.get("id", task_id)),
            status=Status(status_val),
            result=result.get("result"),
        )

    # Fallback for legacy responses encoded via :class:`GetResult`.
    parsed = Response[GetResult].model_validate(data)
    return TaskInfo(
        id=parsed.result.id, status=Status.running, result=parsed.result.result
    )
