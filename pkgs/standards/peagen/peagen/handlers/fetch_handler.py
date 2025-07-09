# peagen/handlers/fetch_handler.py
"""
Async entry-point for the *fetch* pipeline.

• Delegates heavy-lifting to `peagen.core.fetch_core.fetch_many`.
• Accepts an AutoAPI TaskRead object.
• Returns a lightweight JSON-serialisable summary.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


from autoapi.v2 import AutoAPI
from peagen.orm import Task

from peagen.core.fetch_core import fetch_many

# ─────────────────────────── AutoAPI schema ───────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")  # input model


# ─────────────────────────── main handler ─────────────────────────────
async def fetch_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Parameters expected in *task.payload.args*:

    workspaces           – List[str]  URIs to fetch
    out_dir              – str        destination folder
    repo / ref           – optional git source checkout
    no_source            – bool       passed through to fetch_many
    install_template_sets – bool      passed through
    """
    payload = task.payload or {}
    args: Dict[str, Any] = payload.get("args", {})

    uris: List[str] = args.get("workspaces", [])
    repo: Optional[str] = args.get("repo")
    ref: str = args.get("ref", "HEAD")

    summary = fetch_many(
        workspace_uris=uris,
        repo=repo,
        ref=ref,
        out_dir=Path(args["out_dir"]).expanduser(),
        install_template_sets_flag=args.get("install_template_sets", True),
        no_source=args.get("no_source", False),
    )
    return summary  # plain dict – AutoAPI will store it
