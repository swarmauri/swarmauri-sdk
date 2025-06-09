"""Async entry-point for the mutate workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from peagen.core.mutate_core import mutate_workspace
from peagen.models import Task


async def mutate_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})

    result = mutate_workspace(
        workspace_uri=args["workspace_uri"],
        target_file=args["target_file"],
        import_path=args["import_path"],
        entry_fn=args["entry_fn"],
        gens=int(args.get("gens", 1)),
        profile_mod=args.get("profile_mod"),
        cfg_path=Path(args["config"]) if args.get("config") else None,
    )
    return result

