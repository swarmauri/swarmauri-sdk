# peagen/handlers/doe_handler.py
from __future__ import annotations

import os
import tempfile
import shutil
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from autoapi.v2 import AutoAPI
from peagen.orm import Task  # ORM class

from peagen.core.doe_core import (
    generate_payload,
    create_factor_branches,
    create_run_branches,
)
from peagen._utils.config_loader import resolve_cfg
from peagen._utils import maybe_clone_repo
from peagen.plugins import PluginManager
from peagen.plugins.vcs import pea_ref

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")  # ← used as input type


# ───────────────────────────  helper fns ──────────────────────────────
def _write_tmp(text: str, suffix: str, tmp_dir: Path) -> Path:
    p = tmp_dir / suffix
    p.write_text(text, encoding="utf-8")
    return p


# ───────────────────────────  main handler  ───────────────────────────
async def doe_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Design-of-Experiments (DoE) worker.

    Parameters
    ----------
    task : TaskRead
        The Task instance whose `payload.action == "doe"`.

    Returns
    -------
    dict
        Result payload to be stored back on the Work / Task row.
    """
    payload = task.payload or {}
    args: Dict[str, Any] = payload.get("args", {})

    # ---------- handle inline spec/template text ----------------------
    tmp_dir: Optional[Path] = None
    if "spec_text" in args or "template_text" in args:
        tmp_dir = Path(tempfile.mkdtemp(prefix="peagen_doe_"))
        if "spec_text" in args:
            args["spec"] = str(_write_tmp(args["spec_text"], "spec.yaml", tmp_dir))
        if "template_text" in args:
            args["template"] = str(
                _write_tmp(args["template_text"], "template.yaml", tmp_dir)
            )

    # ---------- config & plugin manager --------------------------------
    cfg = resolve_cfg(toml_path=args.get("config") or ".peagen.toml")
    pm = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:  # plugin optional
        vcs = None

    # ---------- generate the DoE artefacts ------------------------------
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

    dry_run = result.get("dry_run", args.get("dry_run", False))

    # ---------- optional VCS integration --------------------------------
    if vcs and not dry_run:
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

    # ---------- cleanup -------------------------------------------------
    if tmp_dir:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return result
