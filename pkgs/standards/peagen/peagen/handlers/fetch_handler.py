"""
peagen.handlers.fetch_handler
─────────────────────────────
Async entry-point for the *fetch* pipeline.

• Delegates heavy-lifting to `peagen.core.fetch_core.fetch_many`.
• Accepts an AutoAPI-generated TaskRead object.
• Returns a lightweight JSON-serialisable summary.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from autoapi.v2 import AutoAPI
from peagen.orm  import Task

from peagen.core.fetch_core import fetch_many

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")

# ─────────────────────────── main coroutine ───────────────────────────
async def fetch_handler(task: TaskRead) -> Dict[str, Any]:
    """
    `task.args` MUST contain:

        {
            "workspaces":            [ "<uri>", … ],   # required
            "out_dir":               "<path>",         # required
            "repo":                  "<git url>",      # optional
            "ref":                   "HEAD",           # optional
            "no_source":             bool,
            "install_template_sets": bool
        }
    """
    args: Dict[str, Any] = task.args or {}

    uris: List[str]     = args.get("workspaces", [])
    out_dir: Path       = Path(args["out_dir"]).expanduser()
    repo: Optional[str] = args.get("repo")
    ref:  str           = args.get("ref", "HEAD")

    summary = fetch_many(
        workspace_uris            = uris,
        repo                      = repo,
        ref                       = ref,
        out_dir                   = out_dir,
        install_template_sets_flag= args.get("install_template_sets", True),
        no_source                 = args.get("no_source", False),
    )
    return summary
