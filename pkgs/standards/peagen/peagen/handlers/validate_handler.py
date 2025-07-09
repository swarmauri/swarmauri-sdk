# peagen/handlers/validate_handler.py
"""
Async entry-point for validation tasks.

Input : TaskRead  – AutoAPI schema bound to the Task ORM class
Output: dict      – result returned by validate_core.validate_artifact
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from autoapi.v2 import AutoAPI
from peagen.orm import Task

from peagen._utils import maybe_clone_repo
from peagen.core.validate_core import validate_artifact

# ─────────────────────────── AutoAPI schema ───────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")  # request model


# ─────────────────────────── main coroutine ───────────────────────────
async def validate_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Expected task.payload
    ---------------------
    {
        "args": {
            "kind" : "project" | "template" | ...,
            "path" : "<path-or-uri>",            # optional
            "repo" : "<git-url>",                # optional
            "ref"  : "HEAD"                      # optional, defaults to HEAD
        }
    }
    """
    args: Dict[str, Any] = (task.payload or {}).get("args", {})
    kind: str = args["kind"]  # required
    repo: str | None = args.get("repo")
    ref: str = args.get("ref", "HEAD")
    path_str: str | None = args.get("path")

    with maybe_clone_repo(repo, ref):  # no-op if repo is None
        return validate_artifact(
            kind,
            Path(path_str).expanduser() if path_str else None,        )
