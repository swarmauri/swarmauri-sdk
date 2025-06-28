"""Helpers for building and submitting tasks via the TUI."""

from __future__ import annotations

import httpx
import uuid
from datetime import datetime
import importlib
from typing import Any, Callable, Dict

from peagen.schemas import TaskCreate
from peagen.transport import RPCRequest, RPCResponse
from peagen.defaults import TASK_SUBMIT
from peagen.orm.status import Status


_TASK_BUILDERS: Dict[str, str] = {
    "process": "peagen.cli.commands.process:_build_task",
    "analysis": "peagen.cli.commands.analysis:_build_task",
    "mutate": "peagen.cli.commands.mutate:_build_task",
    "evolve": "peagen.cli.commands.evolve:_build_task",
    "extras": "peagen.cli.commands.extras:_build_task",
    "fetch": "peagen.cli.commands.fetch:_build_task",
}


def _fallback_builder(action: str, args: dict[str, Any], pool: str) -> TaskCreate:
    task = TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool=pool,
        payload={"action": action, "args": args},
        status=Status.queued,
        note="",
        spec_hash="dummy",
        last_modified=datetime.utcnow(),
    )
    task.id = str(task.id)
    return task


def build_task(action: str, args: dict[str, Any], pool: str = "default") -> TaskCreate:
    """Construct a :class:`TaskCreate` using CLI helpers when available."""

    builder_path = _TASK_BUILDERS.get(action)
    if builder_path:
        module_name, func_name = builder_path.split(":")
        module = importlib.import_module(module_name)
        builder: Callable[[dict[str, Any], str], TaskCreate] = getattr(
            module, func_name
        )  # type: ignore[assignment]
        return builder(args, pool)

    return _fallback_builder(action, args, pool)


def submit_task(gateway_url: str, task: TaskCreate) -> dict:
    """Submit *task* to the gateway via JSON-RPC and return the reply."""

    req = RPCRequest(method=TASK_SUBMIT, params=task.model_dump(mode="json"))
    resp = httpx.post(gateway_url, json=req.model_dump(), timeout=30.0)
    resp.raise_for_status()
    return RPCResponse.model_validate(resp.json()).model_dump()
