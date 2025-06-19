# peagen/handlers/doe_handler.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import os

from peagen.core.doe_core import generate_payload  #  ←── renamed import
from peagen.models import Task
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import pea_ref


async def doe_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})

    cfg = resolve_cfg(toml_path=args.get("config", ".peagen.toml"))
    pm = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:  # pragma: no cover - optional
        vcs = None

    result = generate_payload(
        spec_path=Path(args["spec"]).expanduser(),
        template_path=Path(args["template"]).expanduser(),
        output_path=Path(args["output"]).expanduser(),
        cfg_path=Path(args["config"]).expanduser() if args.get("config") else None,
        notify_uri=args.get("notify"),
        dry_run=args.get("dry_run", False),
        force=args.get("force", False),
        skip_validate=args.get("skip_validate", False),
    )

    if vcs and not result.get("dry_run"):
        repo_root = Path(vcs.repo.working_tree_dir)
        rel_paths: List[str] = [os.path.relpath(p, repo_root) for p in result.get("outputs", [])]
        if rel_paths:
            vcs.commit(rel_paths, f"doe {Path(args['spec']).stem}")
            branches = [pea_ref("run", Path(p).stem) for p in result.get("outputs", [])]
            vcs.fan_out("HEAD", branches)

    return result
