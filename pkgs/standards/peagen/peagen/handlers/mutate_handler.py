"""Async entry-point for the mutate workflow."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from peagen.core.mutate_core import mutate_workspace
from peagen.models import Task
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import pea_ref


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
        mutations=args.get("mutations"),
    )

    cfg = resolve_cfg()
    pm = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:  # pragma: no cover - optional
        vcs = None

    if vcs and result.get("winner"):
        repo_root = Path(vcs.repo.working_tree_dir)
        winner_path = Path(result["winner"]).resolve()
        rel = os.path.relpath(winner_path, repo_root)
        vcs.commit([rel], f"mutate {winner_path.name}")
        vcs.create_branch(pea_ref("run", winner_path.stem), checkout=False)

    return result
