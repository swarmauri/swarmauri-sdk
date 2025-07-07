# peagen/handlers/doe_process_handler.py
from __future__ import annotations

import os, shutil, tempfile, uuid, yaml
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

from autoapi.v2          import AutoAPI
from peagen.orm      import Status, Task

from peagen.core.doe_core import generate_payload
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.storage_adapters.file_storage_adapter import FileStorageAdapter

from .fanout import fan_out

# ─────────────────────────── AutoAPI schemas ──────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")               # incoming task


# ─────────────────────────── helper: tmp file -------------------------
def _write_tmp(text: str, fname: str, root: Path) -> Path:
    p = root / fname
    p.write_text(text, encoding="utf-8")
    return p


# ─────────────────────────── main handler  ────────────────────────────
async def doe_process_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Expand a DOE spec (design-of-experiments) and spawn a *process* task
    for every generated project file.

    Parameters
    ----------
    task : TaskRead
        The validated Task row whose `payload.action == "doe_process"`.

    Returns
    -------
    dict
        Result payload containing `children`, `_final_status`, and all fields
        coming back from `generate_payload`.
    """
    payload = task.payload or {}
    args: Dict[str, Any] = payload.get("args", {})

    # ---------- optional repo checkout ---------------------------------
    repo, ref = args.get("repo"), args.get("ref", "HEAD")
    tmp_repo: Optional[Path] = None

    def _resolve_existing(path_str: str) -> Path:
        p = Path(path_str).expanduser()
        if p.exists():
            return p
        alt = Path(__file__).resolve().parents[2] / path_str
        return alt if alt.exists() else p

    if repo:
        from peagen.core.fetch_core import fetch_single

        tmp_repo = Path(tempfile.mkdtemp(prefix="peagen_repo_"))
        fetch_single(repo=repo, ref=ref, dest_root=tmp_repo)

        def _resolve_existing(path_str: str) -> Path:  # type: ignore[override]
            cand = tmp_repo / path_str
            return cand if cand.exists() else Path(path_str)

    # ---------- inline spec / template text ----------------------------
    tmp_data: Optional[Path] = None
    if "spec_text" in args or "template_text" in args:
        tmp_data = Path(tempfile.mkdtemp(prefix="peagen_doe_"))
        if "spec_text" in args:
            args["spec"] = str(_write_tmp(args["spec_text"], "spec.yaml", tmp_data))
        if "template_text" in args:
            args["template"] = str(_write_tmp(args["template_text"], "template.yaml", tmp_data))

    cfg_path = _resolve_existing(args["config"]) if args.get("config") else None

    # ---------- core DoE expansion -------------------------------------
    result = generate_payload(
        spec_path     = _resolve_existing(args["spec"]),
        template_path = _resolve_existing(args["template"]),
        output_path   = Path(args["output"]).expanduser(),
        cfg_path      = cfg_path,
        notify_uri    = args.get("notify"),
        dry_run       = args.get("dry_run", False),
        force         = args.get("force", False),
        skip_validate = args.get("skip_validate", False),
        evaluate_runs = args.get("evaluate_runs", False),
    )

    dry_run = result.get("dry_run", args.get("dry_run", False))
    if dry_run:
        _cleanup(tmp_repo, tmp_data)
        return {"children": [], "_final_status": Status.success.value, **result}

    # ---------- optional object-store upload ---------------------------
    cfg = resolve_cfg(toml_path=str(cfg_path) if cfg_path else ".peagen.toml")
    pm  = PluginManager(cfg)
    try:
        storage_adapter = pm.get("storage_adapters")
    except Exception:                                    # pragma: no cover
        file_cfg = cfg.get("storage", {}).get("adapters", {}).get("file", {})
        storage_adapter = FileStorageAdapter(**file_cfg) if file_cfg else None

    output_paths = result.get("outputs", [])
    projects: List[Tuple[str | bytes, Dict[str, Any]]] = []
    uploaded: List[str] = []

    for p in output_paths:
        text = Path(p).read_text()
        doc  = yaml.safe_load(text)
        proj = (doc.get("PROJECTS") or [None])[0]

        payload: str | bytes = text
        if storage_adapter and not isinstance(storage_adapter, FileStorageAdapter):
            key = Path(p).name
            try:
                with open(p, "rb") as fh:
                    payload = storage_adapter.upload(key, fh)  # type: ignore[attr-defined]
            except Exception:
                payload = text
        if isinstance(payload, str):
            uploaded.append(payload)
        if proj is not None:
            projects.append((payload, proj))

    result["outputs"] = uploaded

    # ---------- spawn process children ---------------------------------
    pool = task.pool
    children: List[Dict[str, Any]] = []
    for payload_blob, proj in projects:
        children.append(
            {
                "id": str(uuid.uuid4()),
                "pool": pool,
                "status": Status.waiting,
                "payload": {
                    "action": "process",
                    "args": {
                        "projects_payload": payload_blob,
                        "project_name": proj.get("NAME"),
                    },
                },
            }
        )

    fan_res = await fan_out(
        task,
        children,
        result=result,
        final_status=Status.waiting,
    )

    _cleanup(tmp_repo, tmp_data)
    return {
        "children": fan_res["children"],
        "_final_status": fan_res["_final_status"],
        **result,
    }


# ───────────────────────── helper: cleanup -----------------------------
def _cleanup(*dirs: Optional[Path]) -> None:
    for d in dirs:
        if d and d.exists():
            shutil.rmtree(d, ignore_errors=True)
