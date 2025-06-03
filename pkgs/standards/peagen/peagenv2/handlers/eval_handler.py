# peagen/handlers/eval_handler.py
"""
Async task-handler for “eval” jobs.

The worker runtime (or a local CLI run) calls this coroutine with
either a plain dict (decoded JSON-RPC) or a peagen.models.Task object.

Returns a JSON-serialisable mapping:
  { "manifest": {…}, "strict_failed": bool }
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from peagen.core.eval_core import evaluate_workspace
from peagen.models import Task  # for typing only


async def eval_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    if not isinstance(task_or_dict, dict):
        task_dict: Dict[str, Any] = json.loads(task_or_dict.model_dump_json())  # type: ignore[arg-type]
    else:
        task_dict = task_or_dict

    args: Dict[str, Any] = task_dict["payload"]["args"]

    manifest = evaluate_workspace(
        workspace_uri=args["workspace_uri"],
        program_glob=args.get("program_glob", "**/*.*"),
        pool_ref=args.get("pool"),
        cfg_path=Path(args["config"]) if args.get("config") else None,
        async_eval=args.get("async_eval", False),
        skip_failed=args.get("skip_failed", False),
    )

    strict = args.get("strict", False)
    strict_failed = strict and any(r["score"] == 0 for r in manifest["results"])

    return {"manifest": manifest, "strict_failed": strict_failed}
