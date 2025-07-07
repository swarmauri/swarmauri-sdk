# peagen/handlers/secrets_handler.py
"""
Async entry-point for secret-management tasks.

Input : TaskRead  – AutoAPI schema for the Task ORM table
Output: dict      – result from secrets_core helpers
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from autoapi.v2          import AutoAPI
from peagen.orm          import Task

from peagen.core import secrets_core

# ─────────────────────────── AutoAPI schema ───────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")                   # incoming model


# ─────────────────────────── main coroutine ───────────────────────────
async def secrets_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Expected *task.payload* structure
    ---------------------------------
    {
        "action": "local-add" | "local-get" | "local-remove"
                | "remote-add" | "remote-get" | "remote-remove",
        "args":   { ... }
    }
    """
    payload: Dict[str, Any] = task.payload or {}
    action:  str | None     = payload.get("action")
    args:    Dict[str, Any] = payload.get("args", {})

    # ─────── local store operations ───────────────────────────────────
    if action == "local-add":
        recipients = [Path(p).expanduser() for p in args.get("recipients", [])]
        secrets_core.add_local_secret(args["name"], args["value"], recipients)
        return {"ok": True}

    if action == "local-get":
        secret = secrets_core.get_local_secret(args["name"])
        return {"secret": secret}

    if action == "local-remove":
        secrets_core.remove_local_secret(args["name"])
        return {"ok": True}

    # ─────── remote (gateway) operations ──────────────────────────────
    gw_url  = args.get("gateway_url", secrets_core.DEFAULT_GATEWAY)
    pool    = args.get("pool", "default")

    if action == "remote-add":
        recipients = [Path(p).expanduser() for p in args.get("recipient", [])]
        return secrets_core.add_remote_secret(
            secret_id = args["secret_id"],
            value     = args["value"],
            gateway_url = gw_url,
            version   = int(args.get("version", 0)),
            recipients= recipients,
            pool      = pool,
        )

    if action == "remote-get":
        secret = secrets_core.get_remote_secret(
            secret_id  = args["secret_id"],
            gateway_url= gw_url,
            pool       = pool,
        )
        return {"secret": secret}

    if action == "remote-remove":
        return secrets_core.remove_remote_secret(
            secret_id  = args["secret_id"],
            gateway_url= gw_url,
            version    = args.get("version"),
            pool       = pool,
        )

    # ─────── unknown action → explicit error ──────────────────────────
    raise ValueError(f"Unknown secret-management action '{action}'")
