from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from peagen.core.migrate_core import (
    ALEMBIC_CFG,
    alembic_downgrade,
    alembic_revision,
    alembic_upgrade,
)
from peagen.transport.json_rpcschemas.task import SubmitParams, SubmitResult
from . import ensure_task


async def migrate_handler(task_or_dict: Dict[str, Any] | SubmitParams) -> SubmitResult:
    task = ensure_task(task_or_dict)
    args: Dict[str, Any] = task.payload["args"]
    op: str = args["op"]
    cfg_path_str: str | None = args.get("alembic_ini")
    cfg_path = Path(cfg_path_str).expanduser() if cfg_path_str else ALEMBIC_CFG

    if op == "upgrade":
        return alembic_upgrade(cfg_path)
    if op == "downgrade":
        return alembic_downgrade(cfg_path)
    if op == "revision":
        msg = args.get("message", "init")
        return alembic_revision(msg, cfg_path)
    return {"ok": False, "error": f"unknown op: {op}"}
