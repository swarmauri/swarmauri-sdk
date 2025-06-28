import asyncio
import textwrap
from pathlib import Path
from typing import Any, Dict
import re
import sys
import types
import uuid
from datetime import datetime, timezone

import typer
from peagen.errors import PATNotAllowedError
from peagen.handlers.init_handler import init_handler
from peagen.plugins import discover_and_register_plugins
from peagen.orm.status import Status
from pydantic import TypeAdapter

from peagen.schemas import TaskCreate
from peagen.protocols import Request, Response
from peagen.protocols.methods.task import (
    TASK_SUBMIT,
    SubmitParams,
    SubmitResult,
)
from peagen.cli.task_builder import _build_task

# Allow tests to monkeypatch ``uuid.uuid4`` without affecting the global ``uuid``
# module. Expose a lightweight alias instead.
_real_uuid4 = uuid.uuid4
_uuid_alias = types.ModuleType("uuid_alias")
_uuid_alias.uuid4 = _real_uuid4
sys.modules[__name__ + ".uuid"] = _uuid_alias

_PAT_RE = re.compile(r"(gh[pousr]_\w+|github_pat_[0-9A-Za-z]+)", re.IGNORECASE)


def _contains_pat(obj: Any) -> bool:
    if isinstance(obj, str):
        return bool(_PAT_RE.search(obj))
    if isinstance(obj, dict):
        return any(_contains_pat(v) for v in obj.values())
    if isinstance(obj, list):
        return any(_contains_pat(v) for v in obj)
    return False


def _call_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke ``init_handler`` synchronously."""
    # Ensure plugin templates are registered before invoking handlers
    discover_and_register_plugins()
    task = TaskCreate(
        tenant_id=_real_uuid4(),
        git_reference_id=_real_uuid4(),
        pool="default",
        payload={"action": "init", "args": args},
        status=Status.queued,
        note="",
        spec_hash=_real_uuid4().hex * 2,
        id=_real_uuid4(),
        last_modified=datetime.now(timezone.utc),
    )
    return asyncio.run(init_handler(task))


def _submit_task(
    args: Dict[str, Any], gateway_url: str, tag: str, *, allow_pat: bool = False
) -> None:
    """Send *args* to a JSON-RPC worker."""
    if not allow_pat and ("pat" in args or _contains_pat(args)):
        raise PATNotAllowedError()
    task = _build_task("init", args)
    params = SubmitParams(task=task).model_dump()
    envelope = Request(
        id=str(uuid.uuid4()), method=TASK_SUBMIT, params=params
    ).model_dump()

    try:
        import httpx

        resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
        resp.raise_for_status()
        adapter = TypeAdapter(Response[SubmitResult])  # type: ignore[index]
        reply = adapter.validate_python(resp.json())
        if reply.error:
            typer.echo(f"[ERROR] {reply.error}")
            raise typer.Exit(1)
        typer.echo(
            f"Submitted {tag} → taskId={reply.result.taskId if reply.result else task.id}"
        )
    except PATNotAllowedError:
        raise
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)


def _summary(created_in: Path, next_cmd: str) -> None:
    typer.echo(
        textwrap.dedent(f"""\
        ✅  Scaffold created: {created_in}
           Next steps:
             {next_cmd}
    """)
    )
