from __future__ import annotations

import uuid
from typing import Any, Dict

import httpx

from pydantic import TypeAdapter

from peagen.transport import Request, Response
from peagen.transport.jsonrpc_schemas import TASK_SUBMIT, Status
from peagen.transport.jsonrpc_schemas.task import SubmitParams, SubmitResult


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


def submit_task(
    gateway_url: str, task: SubmitParams, *, timeout: float = 30.0
) -> Response[SubmitResult]:
    """Submit *task* to *gateway_url* via JSON-RPC and return the typed reply."""

    envelope = Request(
        id=str(uuid.uuid4()), method=TASK_SUBMIT, params=task.model_dump()
    )
    resp = httpx.post(
        gateway_url, json=envelope.model_dump(mode="json"), timeout=timeout
    )
    resp.raise_for_status()
    adapter = TypeAdapter(Response[SubmitResult])  # type: ignore[index]
    return adapter.validate_python(resp.json())
