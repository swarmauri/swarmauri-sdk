# peagen/handlers/doe_handler.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import os

from peagen.core.doe_core import (
    generate_payload,
    create_factor_branches,
    create_run_branches,
)
from peagen.models import Task
from . import ensure_task
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
import yaml


async def doe_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    task = ensure_task(task_or_dict)
    payload = task.payload
    args: Dict[str, Any] = payload.get("args", {})

    cfg = resolve_cfg(toml_path=args.get("config") or ".peagen.toml")
    tmp_dir = None
    if "spec_text" in args or "template_text" in args:
        import tempfile

        tmp_dir = Path(tempfile.mkdtemp(prefix="peagen_data_"))
        if "spec_text" in args:
            spec_file = tmp_dir / "spec.yaml"
            spec_file.write_text(args["spec_text"], encoding="utf-8")
            args["spec"] = str(spec_file)
        if "template_text" in args:
            tmpl_file = tmp_dir / "template.yaml"
            tmpl_file.write_text(args["template_text"], encoding="utf-8")
            args["template"] = str(tmpl_file)
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
        rel_paths: List[str] = [
            os.path.relpath(p, repo_root) for p in result.get("outputs", [])
        ]
        if rel_paths:
            commit_sha = vcs.commit(rel_paths, f"doe {Path(args['spec']).stem}")
            result["commit"] = commit_sha
            vcs.push(vcs.repo.active_branch.name)

        spec_obj = yaml.safe_load(Path(args["spec"]).read_text())
        if spec_obj.get("baseArtifact"):
            spec_dir = Path(args["spec"]).expanduser().parent
            create_factor_branches(vcs, spec_obj, spec_dir)
            create_run_branches(vcs, spec_obj, spec_dir)

    if tmp_dir:
        import shutil

        shutil.rmtree(tmp_dir, ignore_errors=True)
    return result
