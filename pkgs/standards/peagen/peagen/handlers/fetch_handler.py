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
    manifests: List[str]   – one or more manifest URIs
    out_dir:   str | None  – destination workspace folder
    no_source: bool        – skip cloning/copying source packages
    install_template_sets: bool – install template sets (default True)
    """
    # normalise ---------------------------------------------
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})
    manifests: List[str] = args["manifests"]

    summary = fetch_many(
        manifest_uris=manifests,
        out_dir=Path(args["out_dir"]).expanduser() if args.get("out_dir") else None,
        no_source=args.get("no_source", False),
        install_template_sets_flag=args.get("install_template_sets", True),
    )
    return summary
