"""Async entry-point for generating EXTRAS schema files."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from . import ensure_task

from peagen._utils import maybe_clone_repo

from peagen.core.extras_core import generate_schemas
from peagen.transport.json_rpcschemas.task import SubmitParams, SubmitResult
from .repo_utils import fetch_repo, cleanup_repo


async def extras_handler(task_or_dict: Dict[str, Any] | SubmitParams) -> SubmitResult:
    """Generate EXTRAS schemas based on template-set ``EXTRAS.md`` files."""
    task = ensure_task(task_or_dict)
    payload = task.payload
    args: Dict[str, Any] = payload.get("args", {})
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")

    with maybe_clone_repo(repo, ref) as tmp:
        base = tmp or Path(__file__).resolve().parents[1]
        templates_root = (
            Path(args.get("templates_root")).expanduser()
            if args.get("templates_root")
            else base / "template_sets"
        )
        schemas_dir = (
            Path(args.get("schemas_dir")).expanduser()
            if args.get("schemas_dir")
            else base / "jsonschemas" / "extras"
        )
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")
    tmp_dir, prev_cwd = fetch_repo(repo, ref)

    base = Path(__file__).resolve().parents[1]
    templates_root = (
        Path(args.get("templates_root")).expanduser()
        if args.get("templates_root")
        else base / "template_sets"
    )
    schemas_dir = (
        Path(args.get("schemas_dir")).expanduser()
        if args.get("schemas_dir")
        else base / "jsonschemas" / "extras"
    )

    written = generate_schemas(templates_root, schemas_dir)
    if repo:
        cleanup_repo(tmp_dir, prev_cwd)
    return {"generated": [str(p) for p in written]}
