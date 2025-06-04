from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from peagen.core.validate_core import validate_artifact
from peagen.models import Task


async def validate_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    if not isinstance(task_or_dict, dict):
        task_dict: Dict[str, Any] = json.loads(task_or_dict.model_dump_json())  # type: ignore[arg-type]
    else:
        task_dict = task_or_dict

    args: Dict[str, Any] = task_dict["payload"]["args"]
    kind: str = args["kind"]
    path_str: str | None = args.get("path")

    return validate_artifact(kind, Path(path_str).expanduser() if path_str else None)
