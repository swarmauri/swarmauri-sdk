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
    alt = Path(__file__).resolve().parents[2] / path_or_text
    if alt.exists():
        return alt, yaml.safe_load(alt.read_text())
    return None, yaml.safe_load(path_or_text)


async def evolve_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})

    cfg = resolve_cfg()
    pm = PluginManager(cfg)
    try:
        vcs = pm.get("vcs")
    except Exception:  # pragma: no cover - optional
        vcs = None

    spec_path, doc = _load_spec(args["evolve_spec"])
    jobs: List[Dict[str, Any]] = doc.get("JOBS", [])
    mutations = doc.get("operators", {}).get("mutation")

    pool = task_or_dict.get("pool", "default")
    children: List[Task] = []
    for job in jobs:
        if mutations is not None:
            job.setdefault("mutations", mutations)
        children.append(
            Task(
                id=str(uuid.uuid4()),
                pool=pool,
                status=Status.waiting,
                payload={"action": "mutate", "args": job},
            )
        )

    child_ids = await fan_out(
        task_or_dict,
        children,
        result={"evolve_spec": args["evolve_spec"]},
        final_status=Status.waiting,
    )

    if vcs and spec_path:
        repo_root = Path(vcs.repo.working_tree_dir)
        rel_spec = os.path.relpath(spec_path, repo_root)
        vcs.commit([rel_spec], f"evolve {spec_path.stem}")
        branches = [pea_ref("run", cid) for cid in child_ids]
        vcs.fan_out("HEAD", branches)

    return {"children": child_ids, "jobs": len(jobs)}
