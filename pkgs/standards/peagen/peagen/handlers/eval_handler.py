"""
Async task-handler for “eval” jobs.

A worker (or local CLI) calls this coroutine with a `TaskRead` instance.
It returns:

    { "report": {...}, "strict_failed": bool }
"""

from __future__ import annotations

import os
import toml
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Optional

from tigrbl.v3 import get_schema
from peagen.orm import Task

from peagen.core.eval_core import evaluate_workspace
from peagen._utils.config_loader import resolve_cfg

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = get_schema(Task, "read")  # validated input model


# ─────────────────────────── main coroutine ───────────────────────────
async def eval_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Expected *task.args* structure
    ------------------------------
    {
        "program_glob"           : "**/*.*",
        "pool"                   : "<pool ref>",
        "async_eval"             : bool,
        "strict"                 : bool,
        "skip_failed"            : bool,
        "config"                 : "<path toml>",           # optional
        "cfg_override"           : { ... },                 # optional – inline TOML
        "repo"                   : "<git url>",             # optional
        "ref"                    : "HEAD"                   # optional
    }
    """
    args: Dict[str, Any] = task.args or {}
    cfg_override: Dict[str, Any] = args.get("cfg_override", {})

    repo: Optional[str] = args.get("repo")
    ref: str = args.get("ref", "HEAD")

    cfg_path: Optional[Path] = (
        Path(args["config"]).expanduser() if args.get("config") else None
    )

    # ───── synthesise temporary cfg if override present ───────────────
    tmp_cfg: Optional[NamedTemporaryFile] = None
    if cfg_override or not (cfg_path and cfg_path.exists()):
        cfg = resolve_cfg(toml_text=cfg_override, toml_path=cfg_path or ".peagen.toml")
        tmp_cfg = NamedTemporaryFile("w", suffix=".toml", delete=False)
        tmp_cfg.write(toml.dumps(cfg))
        tmp_cfg.flush()
        cfg_path = Path(tmp_cfg.name)

    # ───── core evaluation ────────────────────────────────────────────
    report = evaluate_workspace(
        repo=repo,
        ref=ref,
        program_glob=args.get("program_glob", "**/*.*"),
        pool_ref=args.get("pool"),
        cfg_path=cfg_path,
        async_eval=args.get("async_eval", False),
        skip_failed=args.get("skip_failed", False),
    )

    # cleanup temporary config, if any
    if tmp_cfg:
        tmp_cfg.close()
        os.unlink(tmp_cfg.name)

    strict = args.get("strict", False)
    strict_failed = strict and any(r["score"] == 0 for r in report["results"])

    return {"report": report, "strict_failed": strict_failed}
