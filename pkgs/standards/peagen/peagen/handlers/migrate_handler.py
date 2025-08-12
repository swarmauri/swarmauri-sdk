"""
peagen.handlers.migrate_handler
───────────────────────────────
Async entry-point for running Alembic migrations.

Input : TaskRead  – AutoAPI schema for the Task ORM table
Output: dict      – result dict from peagen.core.migrate_core
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from autoapi.v2 import get_schema
from peagen.orm import Task

from peagen.core.migrate_core import (
    ALEMBIC_CFG,
    alembic_upgrade,
    alembic_downgrade,
    alembic_revision,
)

# ───────────────────────── Schema handle ──────────────────────────────
TaskRead = get_schema(Task, "read")  # incoming Pydantic model


# ───────────────────────── Main coroutine ─────────────────────────────
async def migrate_handler(task: TaskRead) -> Dict[str, Any]:
    """
    task.args must contain:

        {
            "op"        : "upgrade" | "downgrade" | "revision",
            "alembic_ini": "<optional path>",
            "message"    : "<rev-message, for revision only>"
        }
    """
    args: Dict[str, Any] = task.args or {}  # ← no more payload
    op: str | None = args.get("op")

    if op not in {"upgrade", "downgrade", "revision"}:
        return {"ok": False, "error": f"unknown op: {op}"}

    cfg_path_str: str | None = args.get("alembic_ini")
    cfg_path = Path(cfg_path_str).expanduser() if cfg_path_str else ALEMBIC_CFG

    if op == "upgrade":
        return alembic_upgrade(cfg_path)

    if op == "downgrade":
        return alembic_downgrade(cfg_path)

    # op == "revision"
    message = args.get("message", "init")
    return alembic_revision(message, cfg_path)
