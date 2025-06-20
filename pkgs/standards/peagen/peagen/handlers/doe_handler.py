# peagen/handlers/doe_handler.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import os

from peagen.core.doe_core import (
    generate_payload,
    create_factor_branches,
    create_run_branches,
    _matrix_v2,
)
from peagen.models import Task
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
import yaml


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
        evaluate_runs=args.get("evaluate_runs", False),
    )

    if vcs and not result.get("dry_run"):
        repo_root = Path(vcs.repo.working_tree_dir)
        rel_paths: List[str] = [os.path.relpath(p, repo_root) for p in result.get("outputs", [])]
        if rel_paths:
            vcs.commit(rel_paths, f"doe {Path(args['spec']).stem}")

        spec_obj = yaml.safe_load(Path(args["spec"]).read_text())
        if spec_obj.get("baseArtifact"):
            create_factor_branches(vcs, spec_obj, Path(args["spec"]).expanduser().parent)
            points = _matrix_v2(spec_obj.get("factors", []))
            create_run_branches(vcs, points)

    return result
