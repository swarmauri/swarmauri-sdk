from __future__ import annotations

import uuid
from typing import Any, Dict

import httpx

from peagen.defaults import RPC_TIMEOUT
from peagen.transport import Request, Response, TASK_GET
from peagen.transport.jsonrpc_schemas import TASK_SUBMIT, Status
from peagen.transport.jsonrpc_schemas.task import GetParams, GetResult, SubmitParams


def build_task(
    action: str,
    args: Dict[str, Any],
    *,
    pool: str = "default",
    tenant_id: str | None = None,
    repo: str | None = None,
    ref: str | None = None,
    status: Status = Status.waiting,
    note: str | None = None,
    config_toml: str | None = None,
    labels: list[str] | None = None,
) -> SubmitParams:
    """Return a :class:`SubmitParams` instance for *action* and *args*."""

    if tenant_id is None:
        tenant_id = pool

    return SubmitParams(
        id=str(uuid.uuid4()),
        pool=pool,
        tenant_id=tenant_id,
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
    parsed = Response[GetResult].model_validate(resp.json())
    return parsed.result  # type: ignore[return-value]
