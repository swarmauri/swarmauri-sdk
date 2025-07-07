# task_helpers.py  – new, client-based implementation
from __future__ import annotations

import json, uuid, httpx
from typing import Any, Dict

from autoapi_client import AutoAPIClient
from autoapi.v2      import AutoAPI
from peagen.orm.task import Task                      # ORM
from peagen.defaults import RPC_TIMEOUT
from peagen.orm.task.status import Status

# ------------------------------------------------------------------ #
# local factories  – stay unchanged
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
    tenant_id: str = "default",
    spec_hash: str | None = None,
) -> Any:
    """
    Return a validated *Create* schema instance for the Task resource.
    """
    SCreate = AutoAPI.get_schema(Task, "create")            # dynamic schema
    return SCreate(
        id=str(uuid.uuid4()),
        pool=pool,
        repo=repo,
        ref=ref,
        payload={"action": action, "args": args},
        status=status,
        note=note,
        config_toml=config_toml,
        labels=labels,
        tenant_id=tenant_id,
        spec_hash=spec_hash or uuid.uuid4().hex,
    )


# ------------------------------------------------------------------ #
def submit_task(
    gateway_url: str,
    task: Any,                       # instance returned by build_task
    *,
    timeout: float = RPC_TIMEOUT,
) -> Dict[str, Any]:
    """
    Submit *task* to *gateway_url* via JSON-RPC and return the raw result dict.
    """
    SRead = AutoAPI.get_schema(Task, "read")      # success schema

    try:
        with AutoAPIClient(gateway_url, client=httpx.Client(timeout=timeout)) as rpc:
            res = rpc.call("Tasks.create", params=task, out_schema=SRead)
        return res.model_dump()
    except (httpx.HTTPError, RuntimeError) as exc:
        raise RuntimeError(f"submit_task RPC failed: {exc}") from exc


# ------------------------------------------------------------------ #
def get_task(
    gateway_url: str,
    task_id: str,
    *,
    timeout: float = RPC_TIMEOUT,
):
    """
    Return a validated *Read* model for the task with *task_id*.
    """
    SRead = AutoAPI.get_schema(Task, "read")
    SDel  = AutoAPI.get_schema(Task, "delete")    # only contains primary key

    params = SDel(id=task_id)                     # validate id shape first
    try:
        with AutoAPIClient(gateway_url, client=httpx.Client(timeout=timeout)) as rpc:
            result = rpc.call("Tasks.read", params=params, out_schema=SRead)
        return result
    except (httpx.HTTPError, RuntimeError) as exc:
        raise RuntimeError(f"get_task RPC failed: {exc}") from exc
