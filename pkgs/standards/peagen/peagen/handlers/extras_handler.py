"""
peagen.handlers.extras_handler
──────────────────────────────
Generate JSON-Schema files from template-set ``EXTRAS.md`` sources.

Updates
-------
* **No `maybe_clone_repo`** or ad-hoc cloning logic.
  Caller **must** supply the current task *work-tree* via
  ``task.args["worktree"]``.
* No storage-adapter uploads – files are written directly inside the
  provided work-tree.

Expected ``task.args``
----------------------
{
    "worktree"      : "<abs path>",          # required – task work-tree
    "templates_root": "<dir>",               # optional, default <worktree>/template_sets
    "schemas_dir"   : "<dir>"                # optional, default <worktree>/jsonschemas/extras
}
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from autoapi.v3 import get_schema
from peagen.orm import Task
from peagen.core.extras_core import generate_schemas

# ───────────────────────── schema handle ────────────────────────────
TaskRead = get_schema(Task, "read")


# ───────────────────────── main coroutine ───────────────────────────
async def extras_handler(task: TaskRead) -> Dict[str, Any]:
    args: Dict[str, Any] = task.args or {}

    worktree = Path(args["worktree"]).expanduser().resolve()
    if not worktree.exists():
        raise FileNotFoundError(f"worktree not found: {worktree}")

    templates_root = (
        Path(args["templates_root"]).expanduser()
        if args.get("templates_root")
        else worktree / "template_sets"
    )
    schemas_dir = (
        Path(args["schemas_dir"]).expanduser()
        if args.get("schemas_dir")
        else worktree / "jsonschemas" / "extras"
    )
    schemas_dir.mkdir(parents=True, exist_ok=True)

    written: List[Path] = generate_schemas(templates_root, schemas_dir)
    return {"generated": [str(p) for p in written]}
