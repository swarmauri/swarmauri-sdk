from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from peagen.core.analysis_core import analyze_runs
from peagen.models import Task
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import pea_ref


async def analysis_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})

    run_dirs = [Path(p) for p in args.get("run_dirs", [])]
    spec_name = args.get("spec_name", "analysis")

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
    return result
