# peagen/handlers/eval_handler.py
"""
Async task-handler for “eval” jobs.

A worker (or the CLI during local testing) calls this coroutine with a
`TaskRead` instance.  The function returns a JSON-serialisable mapping:

    { "report": {...}, "strict_failed": bool }
"""

from __future__ import annotations

import os
import toml
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Optional

from autoapi.v2 import AutoAPI
from peagen.orm import Task

from peagen.core.eval_core import evaluate_workspace
from peagen._utils.config_loader import resolve_cfg

# ─────────────────────────── AutoAPI schema ───────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")  # input type


# ─────────────────────────── main handler  ────────────────────────────
async def eval_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Evaluate a workspace as described by *task.payload*.

    Parameters
    ----------
    task : TaskRead
        The Task row whose `payload.action == "eval"`.

    Returns
    -------
    dict
        { "report": {...}, "strict_failed": bool }
    """
    payload = task.payload or {}
    args: Dict[str, Any] = payload.get("args", {})
    cfg_override: Dict[str, Any] = payload.get("cfg_override", {})

    repo: Optional[str] = args.get("repo")
    ref: str = args.get("ref", "HEAD")

    cfg_path: Optional[Path] = (
        Path(args["config"]).expanduser() if args.get("config") else None
    )

    # ---------- synthesise a config file if override provided ----------
    tmp_cfg: Optional[NamedTemporaryFile] = None
    if cfg_override or not (cfg_path and cfg_path.exists()):
        cfg = resolve_cfg(toml_text=cfg_override, toml_path=cfg_path or ".peagen.toml")
        tmp_cfg = NamedTemporaryFile("w", suffix=".toml", delete=False)
        tmp_cfg.write(toml.dumps(cfg))
        tmp_cfg.flush()
        cfg_path = Path(tmp_cfg.name)

    # ---------- core evaluation ----------------------------------------
    report = evaluate_workspace(
        repo=repo,
        ref=ref,
        program_glob=args.get("program_glob", "**/*.*"),
        pool_ref=args.get("pool"),
        cfg_path=cfg_path,
        async_eval=args.get("async_eval", False),
        skip_failed=args.get("skip_failed", False),
    )

    if tmp_cfg:
        tmp_cfg.close()
        os.unlink(tmp_cfg.name)

    strict = args.get("strict", False)
    strict_failed = strict and any(r["score"] == 0 for r in report["results"])

    return {"report": report, "strict_failed": strict_failed}
