# peagen/handlers/eval_handler.py
"""
Async task-handler for “eval” jobs.

The worker runtime (or a local CLI run) calls this coroutine with
either a plain dict (decoded JSON-RPC) or a peagen.transport.jsonrpc_schemas.task.PatchResult object.

Returns a JSON-serialisable mapping:
  { "report": {…}, "strict_failed": bool }
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import toml
from tempfile import NamedTemporaryFile
import os

from peagen.core.eval_core import evaluate_workspace
from peagen._utils.config_loader import resolve_cfg
from peagen.transport.jsonrpc_schemas.task import SubmitParams, SubmitResult
from . import ensure_task


async def eval_handler(task_or_dict: Dict[str, Any] | SubmitParams) -> SubmitResult:
    task = ensure_task(task_or_dict)
    payload = task.payload
    args: Dict[str, Any] = payload.get("args", {})
    cfg_override: Dict[str, Any] = payload.get("cfg_override", {})
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")
    if repo:
        args["workspace_uri"] = f"git+{repo}@{ref}"

    cfg_path = Path(args["config"]) if args.get("config") else None
    tmp: NamedTemporaryFile | None = None
    if cfg_override or not (cfg_path and cfg_path.exists()):
        cfg = resolve_cfg(toml_text=cfg_override, toml_path=cfg_path or ".peagen.toml")
        tmp = NamedTemporaryFile("w", suffix=".toml", delete=False)
        tmp.write(toml.dumps(cfg))
        tmp.flush()
        cfg_path = Path(tmp.name)

    report = evaluate_workspace(
        workspace_uri=args["workspace_uri"],
        program_glob=args.get("program_glob", "**/*.*"),
        pool_ref=args.get("pool"),
        cfg_path=cfg_path,
        async_eval=args.get("async_eval", False),
        skip_failed=args.get("skip_failed", False),
    )

    if tmp:
        tmp.close()
        os.unlink(tmp.name)

    strict = args.get("strict", False)
    strict_failed = strict and any(r["score"] == 0 for r in report["results"])

    return {"report": report, "strict_failed": strict_failed}
