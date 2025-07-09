"""
Generate EXTRAS JSON-Schema files from template-set ``EXTRAS.md`` files.

Input : TaskRead  – AutoAPI schema for the Task table
Output: dict      – { "generated": [ <paths> ] }
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from autoapi.v2 import AutoAPI
from peagen.orm  import Task

from peagen._utils           import maybe_clone_repo
from peagen.core.extras_core import generate_schemas

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")

# ─────────────────────────── main coroutine ───────────────────────────
async def extras_handler(task: TaskRead) -> Dict[str, Any]:
    """
    `task.args` MAY contain:

        repo            – optional git URL
        ref             – optional ref/branch (default "HEAD")
        templates_root  – dir with template-set EXTRAS.md files
        schemas_dir     – destination for generated schema files
    """
    args: Dict[str, Any] = task.args or {}

    repo: Optional[str] = args.get("repo")
    ref:  str           = args.get("ref", "HEAD")

    # ───────── optional repo checkout (context manager cleans up) ─────
    with maybe_clone_repo(repo, ref) as tmp_checkout:
        project_root = tmp_checkout or Path(__file__).resolve().parents[1]

        templates_root = (
            Path(args["templates_root"]).expanduser()
            if args.get("templates_root")
            else project_root / "template_sets"
        )
        schemas_dir = (
            Path(args["schemas_dir"]).expanduser()
            if args.get("schemas_dir")
            else project_root / "jsonschemas" / "extras"
        )

        written: List[Path] = generate_schemas(templates_root, schemas_dir)

    # ───────── return serialisable mapping ────────────────────────────
    return {"generated": [str(p) for p in written]}
