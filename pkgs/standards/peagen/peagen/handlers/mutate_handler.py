"""
Async entry-point for the *mutate* workflow.

Input  : TaskRead  – AutoAPI schema mapped to the Task ORM table
Output : dict      – JSON-serialisable result from mutate_workspace()
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from autoapi.v2 import AutoAPI
from peagen.orm  import Task

from peagen.core.mutate_core   import mutate_workspace
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins            import PluginManager
from peagen.plugins.vcs        import pea_ref

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")

# ─────────────────────────── main coroutine ───────────────────────────
async def mutate_handler(task: TaskRead) -> Dict[str, Any]:
    """
    `task.args` MUST contain:

        {
            "repo"        : "<git url>",          # required
            "ref"         : "HEAD",               # optional
            "target_file" : "<file to mutate>",
            "import_path" : "package.module",
            "entry_fn"    : "main",
            "gens"        : 1,
            "mutations"   : [ {...}, ... ],
            "profile_mod" : "helper.mod",
            "config"      : "<cfg.toml>",         # optional
            "evaluator"   : "<name>",             # plugin name (default 'performance')
            … additional keys forwarded to mutate_core …
        }
    """
    args: Dict[str, Any] = task.args or {}

    # ------------------------------------------------------------------ #
    # 1. Mandatory repository checkout
    # ------------------------------------------------------------------ #
    repo: str           = args["repo"]
    ref:  str           = args.get("ref", "HEAD")

    from peagen.core.fetch_core import fetch_single

    tmp_checkout = Path(tempfile.mkdtemp(prefix="pea_repo_"))
    fetch_single(repo=repo, ref=ref, dest_root=tmp_checkout)

    # The workspace **is** the cloned repository root
    workspace_uri = str(tmp_checkout)

    # ------------------------------------------------------------------ #
    # 2. Resolve configuration & plugins
    # ------------------------------------------------------------------ #
    cfg_path = (
        Path(args["config"]).expanduser() if args.get("config") else None
    )
    cfg = resolve_cfg(toml_path=str(cfg_path) if cfg_path else ".peagen.toml")
    pm  = PluginManager(cfg)

    # evaluator – registry lookup by *name*
    evaluator_name = args.get("evaluator", "performance")
    try:
        evaluator_cls = pm.get("evaluators")[evaluator_name]   # type: ignore
    except Exception:
        raise ValueError(f"Unknown evaluator plugin '{evaluator_name}'")

    # ------------------------------------------------------------------ #
    # 3. Perform mutation
    # ------------------------------------------------------------------ #
    result = mutate_workspace(
        workspace_uri = workspace_uri,
        target_file   = args["target_file"],
        import_path   = args["import_path"],
        entry_fn      = args["entry_fn"],
        gens          = int(args.get("gens", 1)),
        profile_mod   = args.get("profile_mod"),
        cfg_path      = cfg_path,
        mutations     = args.get("mutations"),
        evaluator     = evaluator_cls,          # pass callable/cls, not string
    )

    # ------------------------------------------------------------------ #
    # 4. Optional VCS integration
    # ------------------------------------------------------------------ #
    try:
        vcs = pm.get("vcs")
    except Exception:
        vcs = None

    if vcs and result.get("winner"):
        repo_root    = Path(vcs.repo.working_tree_dir)
        winner_path  = Path(result["winner"]).resolve()
        rel_winner   = os.path.relpath(winner_path, repo_root)

        commit_sha   = vcs.commit([rel_winner], f"mutate {winner_path.name}")
        result["winner_oid"] = vcs.blob_oid(rel_winner)

        branch       = pea_ref("run", winner_path.stem)
        vcs.create_branch(branch, checkout=False)
        vcs.push(branch)

        result.update(commit=commit_sha, branch=branch)

    # ------------------------------------------------------------------ #
    # 5. Cleanup temporary checkout
    # ------------------------------------------------------------------ #
    shutil.rmtree(tmp_checkout, ignore_errors=True)

    return result
