"""
peagen.handlers.doe_handler
───────────────────────────
Asynchronous Design-of-Experiments (*doe*) worker.

Changes vs. legacy
------------------
* **repo / ref are required** – handler always operates in an isolated
  Git *work-tree* created under `repo_lock`.
* **No storage-adapter support**, no legacy *workspace_root* logic.
* Inline YAML (`spec_text`, `template_text`) is still accepted – files are
  written into the work-tree before processing.
"""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import Any, Dict, List

import yaml
from tigrbl.v3 import get_schema
from peagen.orm import Task, Status, Action

from peagen.core.git_repo_core import (
    repo_lock,
    open_repo,
    fetch_git_remote,
    add_git_worktree,
)
from peagen.defaults import ROOT_DIR
from peagen.core.doe_core import (
    generate_payload,
    create_factor_branches,
    create_run_branches,
)
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager

from .fanout import fan_out

# ───────────────────────── schema handle ────────────────────────────
TaskRead = get_schema(Task, "read")


# ───────────────────────── helper -----------------------------------
def _write_inline(text: str, name: str, worktree: Path) -> Path:
    p = worktree / ".peagen" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


# ───────────────────────── handler ----------------------------------
async def doe_handler(task: TaskRead) -> Dict[str, Any]:  # noqa: C901 – orchestrator
    args: Dict[str, Any] = task.args or {}

    # mandatory repo / ref
    repo: str = args["repo"]
    ref: str = args.get("ref", "HEAD")

    # ─── 1. prepare work-tree ───────────────────────────────────────
    repo_hash = hashlib.sha1(repo.encode()).hexdigest()[:12]
    mirror_path = Path(ROOT_DIR).expanduser() / "mirrors" / repo_hash
    worktree = (
        Path(ROOT_DIR).expanduser()
        / "worktrees"
        / repo_hash
        / ref.replace("/", "_")
        / f"doe_{uuid.uuid4().hex[:8]}"
    )
    worktree.parent.mkdir(parents=True, exist_ok=True)

    with repo_lock(repo):
        git_repo = open_repo(mirror_path, remote_url=repo)
        fetch_git_remote(git_repo)
        add_git_worktree(git_repo, ref, worktree)

    # ─── 2. resolve spec / template paths ───────────────────────────
    if "spec_text" in args:
        args["spec"] = str(_write_inline(args["spec_text"], "spec.yaml", worktree))
    if "template_text" in args:
        args["template"] = str(
            _write_inline(args["template_text"], "template.yaml", worktree)
        )

    spec_path = Path(args["spec"]).expanduser()
    template_path = Path(args["template"]).expanduser()
    output_path = Path(args["output"]).expanduser()

    # Any relative paths should be inside the work-tree
    if not spec_path.is_absolute():
        spec_path = (worktree / spec_path).resolve()
    if not template_path.is_absolute():
        template_path = (worktree / template_path).resolve()
    if not output_path.is_absolute():
        output_path = (worktree / output_path).resolve()

    # ─── 3. cfg / plugin manager -----------------------------------
    cfg_path = Path(args["config"]).expanduser() if args.get("config") else None
    cfg = resolve_cfg(toml_path=str(cfg_path) if cfg_path else None)
    pm = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:
        vcs = None

    # ─── 4. generate DoE artefacts ----------------------------------
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

    # ─── 5. optional VCS integration -------------------------------
    if vcs and not result.get("dry_run"):
        repo_root = Path(vcs.repo.working_tree_dir)
        rel_outputs: List[str] = [
            str(Path(p).relative_to(repo_root)) for p in result.get("outputs", [])
        ]
        if rel_outputs:
            commit_sha = vcs.commit(rel_outputs, f"doe {spec_path.stem}")
            result["commit"] = commit_sha
            vcs.push(vcs.repo.active_branch.name)

        # factor / run branches
        spec_obj = yaml.safe_load(spec_path.read_text())
        if spec_obj.get("baseArtifact"):
            create_factor_branches(vcs, spec_obj, spec_path.parent)
            create_run_branches(vcs, spec_obj, spec_path.parent)

    # ─── 6. create child MUTATE tasks via fan_out -------------------
    pool_id = str(getattr(task, "pool_id", "") or "")
    children = [
        {
            "id": str(uuid.uuid4()),
            "pool_id": pool_id,
            "action": Action.MUTATE,
            "status": Status.waiting,
            "args": job,
        }
        for job in result.get("jobs", [])  # generate_payload puts job list here
    ]

    fan = await fan_out(
        parent_task=task,
        child_defs=children,
        result={"doe_spec": str(spec_path)},
        final_status=Status.waiting,
    )
    result.update(children=fan["children"], jobs=len(children))

    return result
