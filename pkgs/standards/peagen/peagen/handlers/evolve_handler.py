# peagen/handlers/evolve_handler.py
"""
Expand an *evolve* specification into many *mutate* child-tasks.

Input : TaskRead  (AutoAPI schema for the Task table)
Output: dict      (serialisable result payload)
"""

from __future__ import annotations

import shutil
import uuid
import yaml
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from autoapi.v2 import AutoAPI
from peagen.orm import Status, Task

from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import pea_ref
from .fanout import fan_out

# ─────────────────────────── AutoAPI schema ───────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")


# ─────────────────────────── helpers ──────────────────────────────────
def _load_spec(path_or_text: str) -> tuple[Optional[Path], dict]:
    """Return (Path if file exists else None, parsed YAML)."""
    path = Path(path_or_text).expanduser()
    if path.exists():
        return path, yaml.safe_load(path.read_text())

    # search ↑ a few repo levels for convenience
    for up in range(2, 6):
        alt = Path(__file__).resolve().parents[up] / path_or_text
        if alt.exists():
            return alt, yaml.safe_load(alt.read_text())
    # treat input as literal YAML
    return None, yaml.safe_load(path_or_text)


def _cleanup(*dirs: Optional[Path]) -> None:
    for d in dirs:
        if d and d.exists():
            shutil.rmtree(d, ignore_errors=True)


# ─────────────────────────── main handler ─────────────────────────────
async def evolve_handler(task: TaskRead) -> Dict[str, Any]:
    payload = task.payload or {}
    args: Dict[str, Any] = payload.get("args", {})

    # ---------- optional repo checkout ---------------------------------
    repo, ref = args.get("repo"), args.get("ref", "HEAD")
    tmp_repo: Optional[Path] = None
    if repo:
        from peagen.core.fetch_core import fetch_single

        tmp_repo = Path(tempfile.mkdtemp(prefix="peagen_repo_"))
        fetch_single(repo=repo, ref=ref, dest_root=tmp_repo)
        spec_path, doc = _load_spec(str((tmp_repo / args["evolve_spec"]).resolve()))
    else:
        spec_path, doc = _load_spec(args["evolve_spec"])

    spec_dir = spec_path.parent if spec_path else Path.cwd()
    jobs: List[Dict[str, Any]] = doc.get("JOBS", [])
    mutations = doc.get("operators", {}).get("mutation")

    cfg = resolve_cfg()
    pm = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:
        vcs = None

    # ---------- utility to resolve local paths -------------------------
    def _resolve_path(p: str) -> str:
        if p.startswith(("git+", "http://", "https://", "/")):
            return p
        resolved = (spec_dir / p).resolve()
        if repo and tmp_repo:
            try:
                return str(resolved.relative_to(tmp_repo))
            except ValueError:  # outside cloned repo
                return str(resolved)
        return str(resolved)

    # ---------- build child mutate-tasks -------------------------------
    pool = task.pool
    children: List[Dict[str, Any]] = []

    for job in jobs:
        if mutations is not None:
            job.setdefault("mutations", mutations)
        if repo:
            job.setdefault("repo", repo)
            job.setdefault("ref", ref)

        # resolve workspace / config / mutation URIs for local runs
        if (ws := job.get("workspace_uri")) and not (
            repo and ws.startswith(("git+", "http", "/"))
        ):
            job["workspace_uri"] = _resolve_path(ws)
        if cfg_path := job.get("config"):
            job["config"] = _resolve_path(cfg_path)
        for mut in job.get("mutations", []):
            if uri := mut.get("uri"):
                mut["uri"] = _resolve_path(uri)

        children.append(
            {
                "id": str(uuid.uuid4()),
                "pool": pool,
                "status": Status.waiting,
                "payload": {"action": "mutate", "args": job},
            }
        )

    # ---------- fan-out helper ----------------------------------------
    fan_res = await fan_out(
        task,
        children,
        result={"evolve_spec": args["evolve_spec"]},
        final_status=Status.waiting,
    )
    child_ids = fan_res["children"]

    # ---------- optional VCS fan-out ----------------------------------
    if vcs and spec_path and repo:
        repo_root = Path(vcs.repo.working_tree_dir)
        try:
            rel_spec = spec_path.resolve().relative_to(repo_root)
        except ValueError:
            rel_spec = None

        if rel_spec is not None:
            commit_sha = vcs.commit([str(rel_spec)], f"evolve {spec_path.stem}")
            branches = [pea_ref("run", cid) for cid in child_ids]
            vcs.fan_out("HEAD", branches)
            if vcs.has_remote():
                for b in branches:
                    vcs.push(b)
            fan_res["commit"] = commit_sha

    # ---------- cleanup & return --------------------------------------
    _cleanup(tmp_repo)
    return {"children": child_ids, "jobs": len(jobs), **fan_res}
