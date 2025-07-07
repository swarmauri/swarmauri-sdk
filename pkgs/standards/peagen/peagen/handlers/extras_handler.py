# peagen/handlers/extras_handler.py
"""
Generate EXTRAS json-schema files from template-set ``EXTRAS.md`` files.

Input : TaskRead  (AutoAPI schema for the Task table)
Output: dict      { "generated": [ ... ] }
"""

from __future__ import annotations

import shutil, tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from autoapi.v2          import AutoAPI
from peagen.orm      import Status, Task

from peagen._utils                 import maybe_clone_repo
from peagen.core.extras_core       import generate_schemas
from .repo_utils                   import fetch_repo, cleanup_repo

# ─────────────────────────── AutoAPI schema ───────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")


# ─────────────────────────── main handler ─────────────────────────────
async def extras_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Generate JSON-Schema files for the “EXTRAS” feature set.

    The handler honours optional arguments in *task.payload.args*:
        • repo / ref               – git source to clone before generation
        • templates_root           – directory containing EXTRAS.md files
        • schemas_dir              – destination folder for generated schemas
    """
    payload = task.payload or {}
    args: Dict[str, Any] = payload.get("args", {})

    repo: Optional[str] = args.get("repo")
    ref:  str           = args.get("ref", "HEAD")

    # ------------------------------------------------------------------
    # 1. Clone repository when requested (context manager cleans up tmp)
    # ------------------------------------------------------------------
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

        # ------------------------------------------------------------------
        # 2. Generate schema files
        # ------------------------------------------------------------------
        written: List[Path] = generate_schemas(templates_root, schemas_dir)

    # ------------------------------------------------------------------
    # 3. Return a simple serialisable mapping
    # ------------------------------------------------------------------
    return {"generated": [str(p) for p in written]}
