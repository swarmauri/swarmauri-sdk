from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from . import ensure_task

from peagen._utils import maybe_clone_repo

from peagen.core.validate_core import validate_artifact
from peagen.transport.json_rpcschemas.task import SubmitParams, SubmitResult


async def validate_handler(task_or_dict: Dict[str, Any] | SubmitParams) -> SubmitResult:
    task = ensure_task(task_or_dict)
    args: Dict[str, Any] = task.payload["args"]
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")
    kind: str = args["kind"]
    path_str: str | None = args.get("path")

    with maybe_clone_repo(repo, ref):
        return validate_artifact(
            kind, Path(path_str).expanduser() if path_str else None
        )
