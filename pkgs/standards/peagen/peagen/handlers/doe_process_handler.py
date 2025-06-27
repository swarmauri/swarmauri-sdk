# peagen/handlers/doe_process_handler.py
"""Handler for DOE workflow that spawns process tasks."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple
import uuid

import yaml

from peagen.core.doe_core import generate_payload
from peagen.models.tasks import Task
from peagen.models import Status
from peagen._utils.config_loader import resolve_cfg
from peagen.plugins import PluginManager
from peagen.plugins.storage_adapters.file_storage_adapter import FileStorageAdapter
from .fanout import fan_out


async def doe_process_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Expand the DOE spec and spawn a process task for each project."""
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")
    tmp_dir = None
    data_dir = None
    if repo:
        from peagen.core.fetch_core import fetch_single
        import tempfile

        tmp_dir = Path(tempfile.mkdtemp(prefix="peagen_repo_"))
        fetch_single(repo=repo, ref=ref, dest_root=tmp_dir)

        def _resolve_existing(path_str: str) -> Path:
            path = Path(path_str)
            cand = tmp_dir / path
            return cand if cand.exists() else path
    else:

        def _resolve_existing(path_str: str) -> Path:
            path = Path(path_str).expanduser()
            if path.exists():
                return path
            alt = Path(__file__).resolve().parents[2] / path_str
            return alt if alt.exists() else path

    if "spec_text" in args or "template_text" in args:
        import tempfile

        data_dir = Path(tempfile.mkdtemp(prefix="peagen_data_"))
        if "spec_text" in args:
            spec_file = data_dir / "spec.yaml"
            spec_file.write_text(args["spec_text"], encoding="utf-8")
            args["spec"] = str(spec_file)
        if "template_text" in args:
            tmpl_file = data_dir / "template.yaml"
            tmpl_file.write_text(args["template_text"], encoding="utf-8")
            args["template"] = str(tmpl_file)

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
        evaluate_runs=args.get("evaluate_runs", False),
    )

    if result.get("dry_run"):
        final = {"children": [], "_final_status": Status.success.value, **result}
        if tmp_dir:
            import shutil

            shutil.rmtree(tmp_dir, ignore_errors=True)
        if data_dir:
            import shutil

            shutil.rmtree(data_dir, ignore_errors=True)
        return final

    cfg = resolve_cfg(toml_path=str(cfg_path) if cfg_path else ".peagen.toml")
    pm = PluginManager(cfg)
    try:
        storage_adapter = pm.get("storage_adapters")
    except Exception:
        file_cfg = cfg.get("storage", {}).get("adapters", {}).get("file", {})
        storage_adapter = FileStorageAdapter(**file_cfg) if file_cfg else None

    output_paths = result.get("outputs", [])
    projects: List[Tuple[str | bytes, Dict[str, Any]]] = []
    uploaded: List[str] = []
    for p in output_paths:
        text = Path(p).read_text()
        doc = yaml.safe_load(text)
        proj = (doc.get("PROJECTS") or [None])[0]
        payload: str | bytes = text
        if (
            storage_adapter
            and not result.get("dry_run")
            and not isinstance(storage_adapter, FileStorageAdapter)
        ):
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

    fan_res = await fan_out(
        task_or_dict, children, result=result, final_status=Status.waiting
    )
    final = {
        "children": fan_res["children"],
        "_final_status": fan_res["_final_status"],
        **result,
    }
    if tmp_dir:
        import shutil

        shutil.rmtree(tmp_dir, ignore_errors=True)
    if data_dir:
        import shutil

        shutil.rmtree(data_dir, ignore_errors=True)
    return final
