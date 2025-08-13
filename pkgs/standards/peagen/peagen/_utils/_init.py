import asyncio
import textwrap
from pathlib import Path
from typing import Any, Dict
import re
import sys
import types
import uuid

import typer
from peagen.handlers.init_handler import init_handler
from peagen.plugins import discover_and_register_plugins
from peagen.defaults import DEFAULT_POOL_ID
from peagen.orm import Action


# Allow tests to monkeypatch ``uuid.uuid4`` without affecting the global ``uuid``
# module. Expose a lightweight alias instead.
_real_uuid4 = uuid.uuid4
_uuid_alias = types.ModuleType("uuid_alias")
_uuid_alias.uuid4 = _real_uuid4
sys.modules[__name__ + ".uuid"] = _uuid_alias
# Expose the alias as ``uuid`` within this module so tests can patch
# ``peagen._utils._init.uuid.uuid4`` without affecting the real ``uuid`` module.
uuid = _uuid_alias

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
    """Invoke :func:`init_handler` synchronously."""

    discover_and_register_plugins()
    from peagen.cli.task_helpers import build_task

    task = build_task(
        action=Action.FETCH,
        args=args,
        pool_id=str(DEFAULT_POOL_ID),
        repo="local",
        ref="HEAD",
    )
    task = task.model_copy(update={"id": str(_uuid_alias.uuid4())})
    return asyncio.run(init_handler(task))


def _summary(created_in: Path, next_cmd: str) -> None:
    typer.echo(
        textwrap.dedent(f"""\
        ✅  Scaffold created: {created_in}
           Next steps:
             {next_cmd}
    """)
    )
