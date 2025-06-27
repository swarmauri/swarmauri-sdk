# peagen/handlers/fetch_handler.py
"""
Async entry-point for the *fetch* pipeline.

• Accepts either a plain dict (decoded JSON-RPC) or a peagen.orm.Task.
• Delegates all heavy-lifting to core.fetch_core.fetch_many().
• Returns a lightweight JSON-serialisable summary.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from . import ensure_task

from peagen.core.fetch_core import fetch_many
from peagen.orm import Task  # for type hints only


async def fetch_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    """
    Parameters (in task.payload.args)
    ---------------------------------
    workspaces: List[str]  – one or more workspace URIs
    out_dir:   str        – destination workspace folder
    no_source: bool        – ignored
    install_template_sets: bool – ignored
    """
    # normalise ---------------------------------------------
    task = ensure_task(task_or_dict)
    payload = task.payload
    args: Dict[str, Any] = payload.get("args", {})
    uris: List[str] = args.get("workspaces", [])
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")

    summary = fetch_many(
        workspace_uris=uris,
        repo=repo,
        ref=ref,
        out_dir=Path(args["out_dir"]).expanduser(),
        install_template_sets_flag=args.get("install_template_sets", True),
        no_source=args.get("no_source", False),
    )
    return summary
