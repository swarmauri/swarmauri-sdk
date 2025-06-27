from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from peagen._utils import maybe_clone_repo

from peagen.core.validate_core import validate_artifact
from peagen.models.tasks import Task


async def validate_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    if not isinstance(task_or_dict, dict):
        task_dict: Dict[str, Any] = json.loads(task_or_dict.model_dump_json())
    else:
        task_dict = task_or_dict

    args: Dict[str, Any] = task_dict["payload"]["args"]
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")
    kind: str = args["kind"]
    path_str: str | None = args.get("path")

    with maybe_clone_repo(repo, ref):
        return validate_artifact(
            kind, Path(path_str).expanduser() if path_str else None
        )
