import textwrap
from pathlib import Path
from typing import Any
import re
import sys
import types
import uuid

import typer


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


def _summary(created_in: Path, next_cmd: str) -> None:
    typer.echo(
        textwrap.dedent(f"""\
        ✅  Scaffold created: {created_in}
           Next steps:
             {next_cmd}
    """)
    )
