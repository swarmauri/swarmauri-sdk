"""Async entry-point for generating EXTRAS schema files."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from peagen.core.extras_core import generate_schemas
from peagen.models import Task


async def extras_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Generate EXTRAS schemas based on template-set ``EXTRAS.md`` files."""
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})

    base = Path(__file__).resolve().parents[1]
    templates_root = (
        Path(args.get("templates_root")).expanduser()
        if args.get("templates_root")
        else base / "template_sets"
    )
    schemas_dir = (
        Path(args.get("schemas_dir")).expanduser()
        if args.get("schemas_dir")
        else base / "schemas" / "extras"
    )

    written = generate_schemas(templates_root, schemas_dir)
    return {"generated": [str(p) for p in written]}
