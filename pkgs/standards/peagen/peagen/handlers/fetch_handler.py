# peagen/handlers/fetch_handler.py
"""
Async entry-point for the *fetch* pipeline.

• Accepts either a plain dict (decoded JSON-RPC) or a peagen.models.Task.
• Delegates all heavy-lifting to core.fetch_core.fetch_many().
• Returns a lightweight JSON-serialisable summary.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from peagen.core.fetch_core import fetch_many
from peagen.models import Task  # for type hints only


async def fetch_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    """
    Parameters (in task.payload.args)
    ---------------------------------
    workspaces: List[str]  – one or more workspace URIs
    out_dir:   str | None  – destination workspace folder
    no_source: bool        – ignored
    install_template_sets: bool – ignored
    """
    # normalise ---------------------------------------------
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})
    uris: List[str] = args.get("workspaces") or args.get("manifests", [])

    summary = fetch_many(
        workspace_uris=uris,
        out_dir=Path(args["out_dir"]).expanduser() if args.get("out_dir") else None,
    )
    return summary
