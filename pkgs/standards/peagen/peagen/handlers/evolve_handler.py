"""Fan-out evolve spec into multiple mutate tasks."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from peagen.models import Task
from peagen.handlers.fanout import fanout


async def evolve_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Expand EVOLVE spec and spawn mutate tasks."""
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})

    spec_path = Path(args["evolve_spec"]).expanduser()
    doc = yaml.safe_load(spec_path.read_text())
    mutations: List[Dict[str, Any]] = doc.get("MUTATIONS", [])

    return await fanout(task_or_dict, "mutate", mutations, {"evolve_spec": str(spec_path)})
