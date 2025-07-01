# peagen/handlers/fetch_handler.py
"""
Async entry-point for the *fetch* pipeline.

• Delegates all heavy-lifting to ``core.fetch_core.fetch_many``.
• Returns a lightweight JSON-serialisable summary.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


from peagen.core.fetch_core import fetch_many
from peagen.transport.jsonrpc_schemas.task import SubmitParams, SubmitResult


async def fetch_handler(task: SubmitParams) -> SubmitResult:
    """
    Parameters (in task.payload.args)
    ---------------------------------
    workspaces: List[str]  – one or more workspace URIs
    out_dir:   str        – destination workspace folder
    no_source: bool        – ignored
    install_template_sets: bool – ignored
    """
    # normalise ---------------------------------------------
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
