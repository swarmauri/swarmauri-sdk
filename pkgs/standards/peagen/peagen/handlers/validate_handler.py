"""
peagen.handlers.validate_handler
────────────────────────────────
Async entry-point for generic *validate* tasks (schema / semantic checks).

Changes vs. legacy
------------------
* **worktree required** – handler operates inside an existing task
  work-tree supplied via ``task.args["worktree"]``; no cloning logic.
* Removes the `maybe_clone_repo` context manager and any repo-checkout code.
* Calls :pyfunc:`peagen.core.validate_core.validate_artifact` directly.

Expected ``task.args``
----------------------
{
    "kind":      "project" | "template" | ... ,   # required
    "worktree":  "<abs path>",                    # required – task work-tree
    "path":      "<relative|abs path>"            # optional, defaults to CWD within work-tree
}
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

from autoapi.v3 import get_schema
from peagen.orm import Task
from peagen.core.validate_core import validate_artifact

# ───────────────────────── schema handle ────────────────────────────
TaskRead = get_schema(Task, "read")


# ───────────────────────── main coroutine ───────────────────────────
async def validate_handler(task: TaskRead) -> Dict[str, Any]:
    args: Dict[str, Any] = task.args or {}

    kind: str = args["kind"]  # validation target type (mandatory)
    worktree = Path(args["worktree"]).expanduser().resolve()
    if not worktree.exists():
        raise FileNotFoundError(f"worktree not found: {worktree}")

    # Resolve the artifact path (may be omitted for some kinds)
    artifact_path_arg = args.get("path")
    artifact_path: Path | None = None
    if artifact_path_arg:
        p = Path(artifact_path_arg).expanduser()
        artifact_path = p if p.is_absolute() else (worktree / p).resolve()

    # Delegate to core validator
    return validate_artifact(kind, artifact_path)
