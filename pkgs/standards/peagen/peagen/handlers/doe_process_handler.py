# peagen/handlers/doe_process_handler.py
"""Handler for DOE workflow that spawns process tasks."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple
import uuid

import yaml

from peagen.core.doe_core import generate_payload
from peagen.models import Task, Status
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.storage_adapters.file_storage_adapter import FileStorageAdapter
from .fanout import fan_out


async def doe_process_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Expand the DOE spec and spawn a process task for each project."""
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})

    def _resolve_existing(path_str: str) -> Path:
        path = Path(path_str).expanduser()
        if path.exists():
            return path
        alt = Path(__file__).resolve().parents[2] / path_str
        return alt if alt.exists() else path

    cfg_path = _resolve_existing(args["config"]) if args.get("config") else None

    result = generate_payload(
        spec_path=_resolve_existing(args["spec"]),
        template_path=_resolve_existing(args["template"]),
        output_path=Path(args["output"]).expanduser(),
        cfg_path=cfg_path,
        notify_uri=args.get("notify"),
        dry_run=args.get("dry_run", False),
        force=args.get("force", False),
        skip_validate=args.get("skip_validate", False),
    )

    cfg = resolve_cfg(toml_path=str(cfg_path) if cfg_path else ".peagen.toml")
    pm = PluginManager(cfg)
    try:
        storage_adapter = pm.get("storage_adapters")
    except Exception:
        file_cfg = (
            cfg.get("storage", {})
            .get("adapters", {})
            .get("file", {})
        )
        storage_adapter = FileStorageAdapter(**file_cfg) if file_cfg else None

    output_paths = result.get("outputs", [])
    projects: List[Tuple[str | bytes, Dict[str, Any]]] = []
    uploaded: List[str] = []
    for p in output_paths:
        text = Path(p).read_text()
        doc = yaml.safe_load(text)
        proj = (doc.get("PROJECTS") or [None])[0]
        payload: str | bytes = text
        if storage_adapter and not result.get("dry_run") and not isinstance(storage_adapter, FileStorageAdapter):
            key = f"{Path(p).name}"
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

    pool = task_or_dict.get("pool", "default")
    children: List[Task] = []
    for path, proj in projects:
        children.append(
            Task(
                id=str(uuid.uuid4()),
                pool=pool,
                action="process",
                status=Status.waiting,
                payload={
                    "action": "process",
                    "args": {
                        "projects_payload": path,
                        "project_name": proj.get("NAME"),
                    },
                },
            )
        )

    child_ids = await fan_out(task_or_dict, children, result=result, final_status=Status.waiting)
    return {"children": child_ids, **result}
