"""
peagen.handlers.doe_handler
───────────────────────────
Asynchronous Design-of-Experiments worker.

Input  : TaskRead  – AutoAPI schema for the Task table
Output : dict      – JSON-serialisable result from generate_payload(...)
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from autoapi.v2 import AutoAPI
from peagen.orm  import Task

from peagen.core.doe_core          import (
    generate_payload,
    create_factor_branches,
    create_run_branches,
)
from peagen._utils.config_loader   import resolve_cfg
from peagen.plugins                import PluginManager

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")

# ─────────────────────────── helper fns ───────────────────────────────
def _write_tmp(text: str, suffix: str, tmp_dir: Path) -> Path:
    p = tmp_dir / suffix
    p.write_text(text, encoding="utf-8")
    return p

# ─────────────────────────── main coroutine ───────────────────────────
async def doe_handler(task: TaskRead) -> Dict[str, Any]:
    """
    `task.args` MUST contain
    ------------------------
    {
        "spec"           : "<path>|None",         # OR "spec_text"
        "template"       : "<path>|None",         # OR "template_text"
        "output"         : "<path>",
        "config"         : "<path toml>",
        "notify"         : "<url>",
        "dry_run"        : bool,
        "force"          : bool,
        "skip_validate"  : bool,
        "evaluate_runs"  : bool,
        "repo"           : "<git url>",           # optional (for VCS ops)
        "ref"            : "HEAD"                # optional
    }
    """
    args: Dict[str, Any] = task.args or {}

    # ---------- inline spec / template support -------------------------
    tmp_dir: Optional[Path] = None
    if "spec_text" in args or "template_text" in args:
        tmp_dir = Path(tempfile.mkdtemp(prefix="peagen_doe_"))
        if "spec_text" in args:
            args["spec"] = str(_write_tmp(args["spec_text"], "spec.yaml", tmp_dir))
        if "template_text" in args:
            args["template"] = str(
                _write_tmp(args["template_text"], "template.yaml", tmp_dir)
            )

    # ---------- configuration & plugin manager -------------------------
    cfg = resolve_cfg(toml_path=args.get("config") or ".peagen.toml")
    pm  = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:
        vcs = None

    # ---------- generate DoE artefacts ---------------------------------
    result = generate_payload(
        spec_path     = Path(args["spec"]).expanduser(),
        template_path = Path(args["template"]).expanduser(),
        output_path   = Path(args["output"]).expanduser(),
        cfg_path      = Path(args["config"]).expanduser() if args.get("config") else None,
        notify_uri    = args.get("notify"),
        dry_run       = args.get("dry_run", False),
        force         = args.get("force", False),
        skip_validate = args.get("skip_validate", False),
        evaluate_runs = args.get("evaluate_runs", False),
    )

    # ---------- optional VCS integration -------------------------------
    if vcs and not result.get("dry_run", False):
        repo_root  = Path(vcs.repo.working_tree_dir)
        rel_paths: List[str] = [
            os.path.relpath(p, repo_root) for p in result.get("outputs", [])
        ]
        if rel_paths:
            commit_sha = vcs.commit(rel_paths, f"doe {Path(args['spec']).stem}")
            result["commit"] = commit_sha
            vcs.push(vcs.repo.active_branch.name)

        # create factor / run branches if baseArtifact present
        spec_obj = yaml.safe_load(Path(args["spec"]).read_text())
        if spec_obj.get("baseArtifact"):
            spec_dir = Path(args["spec"]).expanduser().parent
            create_factor_branches(vcs, spec_obj, spec_dir)
            create_run_branches(vcs, spec_obj, spec_dir)

    # ---------- cleanup -
