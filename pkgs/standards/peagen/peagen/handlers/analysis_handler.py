from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from peagen._utils import maybe_clone_repo

from peagen.core.analysis_core import analyze_runs
from peagen.protocols.methods.task import PatchResult
from . import ensure_task
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import pea_ref
from .repo_utils import fetch_repo, cleanup_repo


async def analysis_handler(
    task_or_dict: Dict[str, Any] | PatchResult,
) -> Dict[str, Any]:
    task = ensure_task(task_or_dict)
    payload = task.payload
    args: Dict[str, Any] = payload.get("args", {})
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")

    repo = args.get("repo")
    ref = args.get("ref", "HEAD")
    tmp_dir, prev_cwd = fetch_repo(repo, ref)

    run_dirs = [Path(p) for p in args.get("run_dirs", [])]
    spec_name = args.get("spec_name", "analysis")

    with maybe_clone_repo(repo, ref):
        result = analyze_runs(run_dirs, spec_name=spec_name)

    cfg = resolve_cfg()
    pm = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:  # pragma: no cover - optional
        vcs = None

    if vcs:
        analysis_branch = pea_ref("analysis", spec_name)
        vcs.create_branch(analysis_branch, "HEAD", checkout=True)
        for rd in run_dirs:
            run_branch = pea_ref("run", Path(rd).name)
            vcs.merge_ours(run_branch, f"merge {run_branch}")
        if result.get("results_file"):
            repo_root = Path(vcs.repo.working_tree_dir)
            rel = Path(result["results_file"]).resolve().relative_to(repo_root)
            commit_sha = vcs.commit([str(rel)], f"analysis {spec_name}")
            result["commit"] = commit_sha
        vcs.switch("HEAD")
        vcs.push(analysis_branch)
        result["analysis_branch"] = analysis_branch
    if repo:
        cleanup_repo(tmp_dir, prev_cwd)
    return result
