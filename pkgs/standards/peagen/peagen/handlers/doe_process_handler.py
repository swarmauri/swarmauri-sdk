"""
peagen.handlers.doe_process_handler
───────────────────────────────────
Expand a DOE specification into many *process* child-tasks.

Differences from legacy version
-------------------------------
* **Work-tree first** – no ad-hoc clones or tmp repos; uses mirror +
  `git worktree` under `repo_lock`.
* **No storage adapters** – artefacts stay in the repository.
* Removes all support for legacy `workspace_uri`.
"""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import Any, Dict, List

import yaml
from tigrbl.v3 import get_schema
from peagen.orm import Task, Status, Action

from peagen.defaults import ROOT_DIR
from peagen.core.git_repo_core import (
    repo_lock,
    open_repo,
    fetch_git_remote,
    add_git_worktree,
)
from peagen.core.doe_core import generate_payload
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import pea_ref
from .fanout import fan_out

# ─────────────────────────── schema handle ──────────────────────────
TaskRead = get_schema(Task, "read")


# ─────────────────────────── helpers ────────────────────────────────
def _resolve_in_tree(p: str | Path, tree: Path) -> Path:
    """Return absolute path inside *tree* (if relative)."""
    p = Path(p).expanduser()
    return p if p.is_absolute() else (tree / p).resolve()


# ─────────────────────────── main coroutine ─────────────────────────
async def doe_process_handler(task: TaskRead) -> Dict[str, Any]:  # noqa: C901
    args: Dict[str, Any] = task.args or {}

    repo: str = args["repo"]
    ref: str = args.get("ref", "HEAD")

    # ── 1. materialise work-tree ─────────────────────────────────────
    repo_hash = hashlib.sha1(repo.encode()).hexdigest()[:12]
    mirror_path = Path(ROOT_DIR).expanduser() / "mirrors" / repo_hash
    worktree = (
        Path(ROOT_DIR).expanduser()
        / "worktrees"
        / repo_hash
        / ref.replace("/", "_")
        / f"doe_proc_{uuid.uuid4().hex[:8]}"
    )
    worktree.parent.mkdir(parents=True, exist_ok=True)

    with repo_lock(repo):
        r = open_repo(mirror_path, remote_url=repo)
        fetch_git_remote(r)
        add_git_worktree(r, ref, worktree)

    # ── 2. locate spec / template inside work-tree ───────────────────
    spec_path = _resolve_in_tree(args["spec"], worktree)
    template_path = _resolve_in_tree(args["template"], worktree)
    output_path = _resolve_in_tree(args["output"], worktree)
    cfg_path = (
        _resolve_in_tree(args["config"], worktree) if args.get("config") else None
    )

    # ── 3. DOE expansion ─────────────────────────────────────────────
    result = generate_payload(
        spec_path=spec_path,
        template_path=template_path,
        output_path=output_path,
        cfg_path=cfg_path,
        dry_run=args.get("dry_run", False),
        force=args.get("force", False),
        skip_validate=args.get("skip_validate", False),
        evaluate_runs=args.get("evaluate_runs", False),
    )

    # short-circuit dry-run
    if result.get("dry_run"):
        return {"children": [], "_final_status": Status.success.value, **result}

    # ── 4. child PROCESS tasks ---------------------------------------
    pool_id = str(getattr(task, "pool_id", "") or "")
    children: List[Dict[str, Any]] = []

    for payload_file in result.get("outputs", []):
        doc = yaml.safe_load(Path(payload_file).read_text())
        proj_first = (doc.get("PROJECTS") or [None])[0]
        children.append(
            {
                "id": str(uuid.uuid4()),
                "pool_id": pool_id,
                "action": Action.PROCESS,
                "status": Status.waiting,
                "args": {
                    "projects_payload": Path(payload_file).read_text(),
                    "project_name": proj_first.get("NAME") if proj_first else None,
                    "worktree": str(worktree),  # pass downstream for commit sync
                },
            }
        )

    fan = await fan_out(
        parent_task=task,
        child_defs=children,
        result=result,
        final_status=Status.waiting,
    )

    # ── 5. optional VCS integration ----------------------------------
    cfg = resolve_cfg(toml_path=str(cfg_path) if cfg_path else None)
    pm = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:
        vcs = None

    if vcs:
        repo_root = Path(vcs.repo.working_tree_dir)
        rel_outputs = [
            str(Path(p).resolve().relative_to(repo_root))
            for p in result.get("outputs", [])
        ]
        if rel_outputs:
            commit_sha = vcs.commit(rel_outputs, f"doe_process {spec_path.stem}")
            result["commit"] = commit_sha
            vcs.push(vcs.repo.active_branch.name)
            branches = [pea_ref("run", cid) for cid in fan["children"]]
            vcs.fan_out("HEAD", branches)
            if vcs.has_remote():
                for b in branches:
                    vcs.push(b)

    # ── 6. final response --------------------------------------------
    return {
        "children": fan["children"],
        "_final_status": fan["_final_status"],
        **result,
    }
