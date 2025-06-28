"""Async entry-point for the mutate workflow."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from . import ensure_task

from peagen.core.mutate_core import mutate_workspace
from peagen.schemas import TaskRead
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import pea_ref


async def mutate_handler(task: TaskRead) -> Dict[str, Any]:
    task = ensure_task(task)
    payload = task.payload
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
            from peagen.core.mirror_core import open_repo

            vcs = open_repo(tmp_dir)
        else:
            vcs = None

    if vcs and result.get("winner"):
        repo_root = Path(vcs.repo.working_tree_dir)
        winner_path = Path(result["winner"]).resolve()
        rel = os.path.relpath(winner_path, repo_root)
        commit_sha = None
        branch = None
        if vcs.repo.head.is_valid() and winner_path.exists():
            commit_sha = vcs.commit([rel], f"mutate {winner_path.name}")
            result["winner_oid"] = vcs.blob_oid(rel)
            branch = pea_ref("run", winner_path.stem)
            vcs.create_branch(branch, checkout=False)
            vcs.push(branch)
        if commit_sha is not None:
            result["commit"] = commit_sha
        if branch:
            result["branch"] = branch
    if tmp_dir:
        import shutil

        shutil.rmtree(tmp_dir, ignore_errors=True)
    return result
