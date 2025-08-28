"""
peagen.handlers.fetch_handler
─────────────────────────────
Async entry-point for the *fetch* pipeline.

• Delegates work to :func:`peagen.core.fetch_core.fetch_many`.
• Accepts an AutoAPI-generated **TaskRead** object whose ``args`` must contain:

    {
        "repos":   [ "<git-url>", … ],   # required – list of clone URLs
        "ref":     "main",               # optional – branch/tag/SHA (default "HEAD")
        "out_dir": "<path>"              # optional – base directory for work-trees
    }

Returns a JSON-serialisable summary produced by *fetch_many*.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from autoapi.v3 import get_schema
from peagen.orm import Task
from peagen.core.fetch_core import fetch_many

# ────────────────────────── schema handle ───────────────────────────
TaskRead = get_schema(Task, "read")


# ─────────────────────────── coroutine ──────────────────────────────
async def fetch_handler(task: TaskRead) -> Dict[str, Any]:
    args: Dict[str, Any] = task.args or {}

    repos: List[str] = args.get("repos", [])
    if not repos:
        raise ValueError("task.args.repos must be a non-empty list of clone URLs")

    ref: str = args.get("ref", "HEAD")
    out_dir_arg: Optional[str] = args.get("out_dir")
    out_dir: Optional[Path] = Path(out_dir_arg).expanduser() if out_dir_arg else None

    summary = fetch_many(repos=repos, ref=ref, out_dir=out_dir)
    return summary
