"""Expand an evolve spec into multiple mutate tasks."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, List
import os

import yaml

from peagen.models import Task, Status
from .fanout import fan_out
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.vcs import pea_ref


def _load_spec(path_or_text: str) -> tuple[Path | None, dict]:
    """Return a tuple of (Path | None, parsed YAML)."""
    path = Path(path_or_text).expanduser()
    if path.exists():
        return path, yaml.safe_load(path.read_text())
    alt_candidates = [
        Path(__file__).resolve().parents[2] / path_or_text,
        Path(__file__).resolve().parents[3] / path_or_text,
        Path(__file__).resolve().parents[4] / path_or_text,
        Path(__file__).resolve().parents[5] / path_or_text,
    ]
    for alt in alt_candidates:
        if alt.exists():
            return alt, yaml.safe_load(alt.read_text())
    return None, yaml.safe_load(path_or_text)


async def evolve_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
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
        spec_path, doc = _load_spec(str((tmp_dir / args["evolve_spec"]).resolve()))
    else:
        spec_path, doc = _load_spec(args["evolve_spec"])

    cfg = resolve_cfg()
    pm = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:  # pragma: no cover - optional
        vcs = None

    spec_dir = spec_path.parent if spec_path else Path.cwd()
    jobs: List[Dict[str, Any]] = doc.get("JOBS", [])
    mutations = doc.get("operators", {}).get("mutation")

    pool = task_or_dict.get("pool", "default")

    def _resolve_path(p: str) -> str:
        if p.startswith("git+") or "://" in p or p.startswith("/"):
            return p
        resolved = (spec_dir / p).resolve()
        if repo and tmp_dir:
            try:
                return str(resolved.relative_to(tmp_dir))
            except ValueError:  # pragma: no cover - outside repo
                return str(resolved)
        return str(resolved)

    children: List[Task] = []
    for job in jobs:
        if mutations is not None:
            job.setdefault("mutations", mutations)

        if repo:
            job.setdefault("repo", repo)
            job.setdefault("ref", ref)

        ws = job.get("workspace_uri")
        if ws:
            job_repo = job.get("repo") or repo
            if job_repo:
                job["workspace_uri"] = ws
            else:
                job["workspace_uri"] = _resolve_path(ws)

        cfg = job.get("config")
        if cfg:
            job["config"] = _resolve_path(cfg)

        for mut in job.get("mutations", []):
            uri = mut.get("uri")
            if uri:
                mut["uri"] = _resolve_path(uri)

        children.append(
            Task(
                id=str(uuid.uuid4()),
                pool=pool,
                status=Status.waiting,
                payload={"action": "mutate", "args": job},
            )
        )

    fan_res = await fan_out(
        task_or_dict,
        children,
        result={"evolve_spec": args["evolve_spec"]},
        final_status=Status.waiting,
    )
    child_ids = fan_res["children"]

    if vcs and spec_path:
        repo_root = Path(vcs.repo.working_tree_dir)
        rel_spec = os.path.relpath(spec_path, repo_root)
        commit_sha = vcs.commit([rel_spec], f"evolve {spec_path.stem}")
        branches = [pea_ref("run", cid) for cid in child_ids]
        vcs.fan_out("HEAD", branches)
        for b in branches:
            try:
                vcs.push(b)
            except Exception:  # pragma: no cover - push may fail
                pass
        fan_res["commit"] = commit_sha
    result = {"children": child_ids, "jobs": len(jobs), **fan_res}
    if tmp_dir:
        import shutil

        shutil.rmtree(tmp_dir, ignore_errors=True)
    return result
