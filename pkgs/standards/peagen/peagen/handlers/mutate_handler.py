# peagen/handlers/mutate_handler.py
"""
Async entry-point for the *mutate* workflow.

Input : TaskRead  – AutoAPI schema for the Task ORM table
Output: dict      – JSON-serialisable result from mutate_workspace()
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from autoapi.v2 import AutoAPI
from peagen.orm import Task, Status

from peagen.core.mutate_core import mutate_workspace
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import pea_ref

# ─────────────────────────── AutoAPI schema ───────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")  # incoming model


# ─────────────────────────── main coroutine ──────────────────────────
async def mutate_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Expected task.payload structure
    -------------------------------
    {
        "args": {
            "workspace_uri": "...",
            "target_file"  : "...py",
            "import_path"  : "module.fn",
            "entry_fn"     : "main",
            "gens"         : 1,
            "mutations"    : [...],
            "config"       : "<path>",
            "repo"         : "<git-url>",
            "ref"          : "HEAD",
            # additional evaluator / VCS args …
        }
    }
    """
    args: Dict[str, Any] = (task.payload or {}).get("args", {})
    repo: Optional[str] = args.get("repo")
    ref: str = args.get("ref", "HEAD")

    # ───── optional source checkout ────────────────────────────────────
    tmp_checkout: Optional[Path] = None
    if repo:
        from peagen.core.fetch_core import fetch_single

        tmp_checkout = Path(tempfile.mkdtemp(prefix="pea_repo_"))
        fetch_single(repo=repo, ref=ref, dest_root=tmp_checkout)

        ws_uri = args.get("workspace_uri", ".")
        ws_path = Path(ws_uri)
        # Replace relative workspace path with one inside the checkout
        if not ws_path.is_absolute() and not ws_uri.startswith(
            ("git+", "http", "https", "ssh://")
        ):
            args["workspace_uri"] = str((tmp_checkout / ws_uri).resolve())
        else:
            args["workspace_uri"] = str(ws_uri)

    # ───── perform mutation ────────────────────────────────────────────
    result = mutate_workspace(
        workspace_uri=args["workspace_uri"],
        target_file=args["target_file"],
        import_path=args["import_path"],
        entry_fn=args["entry_fn"],
        gens=int(args.get("gens", 1)),
        profile_mod=args.get("profile_mod"),
        cfg_path=Path(args["config"]).expanduser() if args.get("config") else None,
        mutations=args.get("mutations"),
        evaluator_ref=args.get(
            "evaluator_ref",
            "peagen.plugins.evaluators.performance_evaluator:PerformanceEvaluator",
        ),
    )

    # ───── optional VCS integration ───────────────────────────────────
    cfg = resolve_cfg()
    pm = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:
        vcs = None

    if vcs and result.get("winner"):
        repo_root = Path(vcs.repo.working_tree_dir)
        winner_path = Path(result["winner"]).resolve()
        rel_winner = os.path.relpath(winner_path, repo_root)

        commit_sha = vcs.commit([rel_winner], f"mutate {winner_path.name}")
        result["winner_oid"] = vcs.blob_oid(rel_winner)

        branch = pea_ref("run", winner_path.stem)
        vcs.create_branch(branch, checkout=False)
        vcs.push(branch)

        result.update(commit=commit_sha, branch=branch)

    # ───── cleanup ────────────────────────────────────────────────────
    if tmp_checkout and tmp_checkout.exists():
        shutil.rmtree(tmp_checkout, ignore_errors=True)

    return result
