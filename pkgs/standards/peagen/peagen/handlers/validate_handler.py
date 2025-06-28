from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from peagen._utils import maybe_clone_repo

from peagen.core.validate_core import validate_artifact
from peagen.schemas import TaskRead


async def validate_handler(task: TaskRead) -> Dict[str, Any]:
    args: Dict[str, Any] = task.payload["args"]
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")
    kind: str = args["kind"]
    path_str: str | None = args.get("path")

    with maybe_clone_repo(repo, ref):
        return validate_artifact(
            kind, Path(path_str).expanduser() if path_str else None
        )
