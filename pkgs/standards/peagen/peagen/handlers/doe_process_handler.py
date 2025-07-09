"""
Expand a DOE specification into many *process* child-tasks.

Input : TaskRead  – AutoAPI schema for the Task table
Output: dict      – summary incl. children fan-out result
"""

from __future__ import annotations

import shutil
import tempfile
import uuid
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from autoapi.v2 import AutoAPI
from peagen.orm import Task, Status, Action

from peagen.core.doe_core          import generate_payload
from peagen._utils.config_loader   import resolve_cfg
from peagen.plugins                import PluginManager
from peagen.plugins.storage_adapters.file_storage_adapter import FileStorageAdapter
from .fanout                       import fan_out

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")

# ─────────────────────────── helpers  ─────────────────────────────────
def _write_tmp(text: str, fname: str, root: Path) -> Path:
    p = root / fname
    p.write_text(text, encoding="utf-8")
    return p


def _resolve_existing(path_str: str, repo_root: Optional[Path]) -> Path:
    """Resolve `path_str` against repo checkout if provided."""
    p = Path(path_str).expanduser()
    if p.exists():
        return p
    if repo_root:
        cand = repo_root / path_str
        if cand.exists():
            return cand
    alt = Path(__file__).resolve().parents[2] / path_str
    return alt if alt.exists() else p


def _cleanup(*dirs: Optional[Path]) -> None:
    for d in dirs:
        if d and d.exists():
            shutil.rmtree(d, ignore_errors=True)


# ─────────────────────────── main handler ────────────────────────────
async def doe_process_handler(task: TaskRead) -> Dict[str, Any]:
    args: Dict[str, Any] = task.args or {}

    # -------- optional repo checkout ----------------------------------
    repo, ref = args.get("repo"), args.get("ref", "HEAD")
    tmp_repo: Optional[Path] = None
    if repo:
        from peagen.core.fetch_core import fetch_single
        tmp_repo = Path(tempfile.mkdtemp(prefix="peagen_repo_"))
        fetch_single(repo=repo, ref=ref, dest_root=tmp_repo)

    # -------- inline spec/template text -------------------------------
    tmp_data: Optional[Path] = None
    if "spec_text" in args or "template_text" in args:
        tmp_data = Path(tempfile.mkdtemp(prefix="peagen_doe_"))
        if "spec_text" in args:
            args["spec"] = str(_write_tmp(args["spec_text"], "spec.yaml", tmp_data))
        if "template_text" in args:
            args["template"] = str(
                _write_tmp(args["template_text"], "template.yaml", tmp_data)
            )

    # -------- config path resolution ----------------------------------
    cfg_path: Optional[Path] = None
    if args.get("config"):
        cfg_path = _resolve_existing(args["config"], tmp_repo)

    # -------- core DOE expansion --------------------------------------
    result = generate_payload(
        spec_path   = _resolve_existing(args["spec"], tmp_repo),
        template_path = _resolve_existing(args["template"], tmp_repo),
        output_path = Path(args["output"]).expanduser(),
        cfg_path    = cfg_path,
        dry_run     = args.get("dry_run", False),
        force       = args.get("force", False),
        skip_validate = args.get("skip_validate", False),
        evaluate_runs = args.get("evaluate_runs", False),
    )

    # Short-circuit on dry-run
    if result.get("dry_run", False):
        _cleanup(tmp_repo, tmp_data)
        return {"children": [], "_final_status": Status.success.value, **result}

    # -------- optional object-store upload ----------------------------
    cfg = resolve_cfg(toml_path=str(cfg_path) if cfg_path else ".peagen.toml")
    pm  = PluginManager(cfg)
    try:
        storage_adapter = pm.get("storage_adapters")
    except Exception:                                    # fallback to local file
        file_cfg = cfg.get("storage", {}).get("adapters", {}).get("file", {})
        storage_adapter = FileStorageAdapter(**file_cfg) if file_cfg else None

    uploaded: List[str] = []
    projects: List[Tuple[str | bytes, Dict[str, Any]]] = []

    for p in result.get("outputs", []):
        text = Path(p).read_text()
        doc  = yaml.safe_load(text)
        proj = (doc.get("PROJECTS") or [None])[0]

        payload_blob: str | bytes = text
        if storage_adapter and not isinstance(storage_adapter, FileStorageAdapter):
            key = Path(p).name
            try:
                with open(p, "rb") as fh:
                    payload_blob = storage_adapter.upload(key, fh)  # type: ignore[attr-defined]
            except Exception:
                payload_blob = text

        if isinstance(payload_blob, str):
            uploaded.append(payload_blob)
        if proj is not None:
            projects.append((payload_blob, proj))

    result["outputs"] = uploaded

    # -------- spawn *process* child tasks -----------------------------
    tenant_id = str(getattr(task, "tenant_id", ""))
    pool_id   = str(getattr(task, "pool_id", ""))

    children: List[Dict[str, Any]] = []
    for payload_blob, proj in projects:
        children.append(
            {
                "id":         str(uuid.uuid4()),
                "tenant_id":  tenant_id,
                "pool_id":    pool_id,
                "action":     Action.PROCESS,
                "status":     Status.waiting,
                "args": {
                    "projects_payload": payload_blob,
                    "project_name":     proj.get("NAME") if proj else None,
                },
            }
        )

    fan_res = await fan_out(
        parent_task  = task,
        child_defs   = children,
        result       = result,
        final_status = Status.waiting,
    )

    _cleanup(tmp_repo, tmp_data)
    return {
        "children":      fan_res["children"],
        "_final_status": fan_res["_final_status"],
        **result,
    }
