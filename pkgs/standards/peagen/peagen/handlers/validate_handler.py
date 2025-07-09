"""
Async entry-point for validation tasks.

Input : TaskRead  – AutoAPI schema bound to the Task ORM class
Output: dict      – result from validate_core.validate_artifact
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from autoapi.v2 import AutoAPI
from peagen.orm  import Task

from peagen._utils                import maybe_clone_repo
from peagen.core.validate_core    import validate_artifact

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")        # validated input model


# ─────────────────────────── main coroutine ───────────────────────────
async def validate_handler(task: TaskRead) -> Dict[str, Any]:
    """
    `task.args` MUST contain:

        {
            "kind" : "project" | "template" | ... ,   # required
            "path" : "<path-or-uri>",                 # optional
            "repo" : "<git url>",                     # optional
            "ref"  : "HEAD"                           # optional
        }
    """
    args: Dict[str, Any] = task.args or {}
    kind: str            = args["kind"]                  # required

    repo: Optional[str]  = args.get("repo")
    ref: str             = args.get("ref", "HEAD")
    path_str: Optional[str] = args.get("path")

    with maybe_clone_repo(repo, ref):   # no-op if repo is None
        return validate_artifact(
            kind,
            Path(path_str).expanduser() if path_str else None,
        )
