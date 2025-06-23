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
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")
    tmp_dir = None
    if repo:
        from peagen.core.fetch_core import fetch_single
        import tempfile

        tmp_dir = Path(tempfile.mkdtemp(prefix="peagen_repo_"))
        fetch_single(repo=repo, ref=ref, dest_root=tmp_dir)
        ws = args.get("workspace_uri", ".")
        ws_path = Path(ws)
        if not ws_path.is_absolute() and "://" not in ws and not ws.startswith("git+"):
            args["workspace_uri"] = str((tmp_dir / ws).resolve())
        else:
            args["workspace_uri"] = str(tmp_dir)

    result = mutate_workspace(
        workspace_uri=args["workspace_uri"],
        target_file=args["target_file"],
        import_path=args["import_path"],
        entry_fn=args["entry_fn"],
        gens=int(args.get("gens", 1)),
        profile_mod=args.get("profile_mod"),
        cfg_path=Path(args["config"]) if args.get("config") else None,
        mutations=args.get("mutations"),
        evaluator_ref=args.get(
            "evaluator_ref",
            "peagen.plugins.evaluators.performance_evaluator:PerformanceEvaluator",
        ),
    )

    cfg = resolve_cfg()
    pm = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:  # pragma: no cover - optional
        if tmp_dir and (tmp_dir / ".git").exists():
            from peagen.plugins.vcs import GitVCS

            vcs = GitVCS.open(tmp_dir)
        else:
            vcs = None

    if vcs and result.get("winner"):
        repo_root = Path(vcs.repo.working_tree_dir)
        winner_path = Path(result["winner"]).resolve()
        rel = os.path.relpath(winner_path, repo_root)
        if winner_path.exists():
            commit_sha = vcs.commit([rel], f"mutate {winner_path.name}")
            result["winner_oid"] = vcs.blob_oid(rel)
        else:
            commit_sha = None
        branch = pea_ref("run", winner_path.stem)
        vcs.create_branch(branch, checkout=False)
        vcs.push(branch)
        result["commit"] = commit_sha
        result["branch"] = branch
    if tmp_dir:
        import shutil

        shutil.rmtree(tmp_dir, ignore_errors=True)
    return result
