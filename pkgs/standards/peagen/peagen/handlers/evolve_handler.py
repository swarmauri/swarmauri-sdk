"""
peagen.handlers.evolve_handler
──────────────────────────────
Expand an *evolve* specification into many *mutate* child-tasks.

Assumptions & Guarantees
------------------------
* Caller **must** supply a Git *repo* and *ref* (branch / tag / SHA).
* The handler materialises an isolated **work-tree** using
  `git worktree` under `repo_lock(repo)`.
* No support for legacy `workspace_uri` or storage adapters.
* Returns `{children: [ids…], jobs: <int>, …}` – perfectly serialisable.
"""

from __future__ import annotations

import hashlib
import uuid
import yaml
from pathlib import Path
from typing import Any, Dict, List

from tigrbl.v3 import get_schema
from peagen.orm import Task, Status, Action
from peagen.core.git_repo_core import (
    repo_lock,
    open_repo,
    fetch_git_remote,
    add_git_worktree,
)
from peagen.defaults import ROOT_DIR
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import pea_ref
from .fanout import fan_out

# ────────────────────────────── schema ──────────────────────────────
TaskRead = get_schema(Task, "read")


# ───────────────────────────── helpers ──────────────────────────────
def _load_yaml(path_or_text: str, base: Path) -> Dict[str, Any]:
    """Load YAML from file path (resolved against *base*) or literal text."""
    p = (base / path_or_text).resolve()
    if p.exists():
        return yaml.safe_load(p.read_text()), p
    return yaml.safe_load(path_or_text), None


# ───────────────────────────── handler ──────────────────────────────
async def evolve_handler(task: TaskRead) -> Dict[str, Any]:  # noqa: C901 – orchestrator
    args: Dict[str, Any] = task.args or {}
    repo: str = args["repo"]  # required
    ref: str = args.get("ref", "HEAD")

    # ─── 1. create mirror + work-tree ────────────────────────────────
    repo_hash = hashlib.sha1(repo.encode()).hexdigest()[:12]
    mirror_path = Path(ROOT_DIR).expanduser() / "mirrors" / repo_hash
    worktree_root = (
        Path(ROOT_DIR).expanduser()
        / "worktrees"
        / repo_hash
        / ref.replace("/", "_")
        / f"evolve_{uuid.uuid4().hex[:8]}"
    )
    worktree_root.parent.mkdir(parents=True, exist_ok=True)

    with repo_lock(repo):
        git_repo = open_repo(mirror_path, remote_url=repo)
        fetch_git_remote(git_repo)
        add_git_worktree(git_repo, ref, worktree_root)

    # ─── 2. load evolve spec -----------------------------------------
    spec_rel = args["evolve_spec"]
    spec_doc, spec_file = _load_yaml(spec_rel, worktree_root)
    jobs: List[Dict[str, Any]] = spec_doc.get("JOBS", [])
    mutations = spec_doc.get("operators", {}).get("mutation")

    # ─── 3. plugin manager & VCS -------------------------------------
    cfg = resolve_cfg()
    pm = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:
        vcs = None

    # ─── 4. build child mutate tasks ---------------------------------
    pool_id = str(getattr(task, "pool_id", "") or "")
    children: List[Dict[str, Any]] = []

    for job in jobs:
        # inherit global mutation operators
        if mutations is not None:
            job.setdefault("mutations", mutations)

        # ensure repo/ref present
        job.setdefault("repo", repo)
        job.setdefault("ref", ref)

        # resolve any relative paths against work-tree root
        for key in ("config", "target_file"):
            if key in job and not Path(job[key]).is_absolute():
                job[key] = str((worktree_root / job[key]).resolve())

        children.append(
            {
                "id": str(uuid.uuid4()),
                "pool_id": pool_id,
                "action": Action.MUTATE,
                "status": Status.waiting,
                "args": job,
            }
        )

    # ─── 5. fan-out ---------------------------------------------------
    fan = await fan_out(
        parent_task=task,
        child_defs=children,
        result={"evolve_spec": spec_rel},
        final_status=Status.waiting,
    )
    child_ids = fan["children"]

    # ─── 6. optional VCS commit / branch fan-out ----------------------
    if vcs and spec_file is not None:
        repo_root = Path(vcs.repo.working_tree_dir)
        try:
            rel_spec = spec_file.relative_to(repo_root)
        except ValueError:
            rel_spec = None

        if rel_spec is not None:
            commit_sha = vcs.commit([str(rel_spec)], f"evolve {spec_file.stem}")
            branches = [pea_ref("run", cid) for cid in child_ids]
            vcs.fan_out("HEAD", branches)
            if vcs.has_remote():
                for b in branches:
                    vcs.push(b)
            fan["commit"] = commit_sha

    # ─── 7. done ------------------------------------------------------
    return {"children": child_ids, "jobs": len(jobs), **fan}
