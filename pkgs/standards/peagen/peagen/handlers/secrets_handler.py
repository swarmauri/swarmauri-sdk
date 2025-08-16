"""
peagen.handlers.secrets_handler
───────────────────────────────
Async entry-point for secret-management tasks.

Input : TaskRead  – AutoAPI schema for the Task table
Output: dict      – result from peagen.core.secrets_core helpers
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from autoapi.v3 import get_schema
from peagen.orm import Task

from peagen.core import secrets_core

# ─────────────────────────── schema handle ────────────────────────────
TaskRead = get_schema(Task, "read")


# ─────────────────────────── main coroutine ───────────────────────────
async def secrets_handler(task: TaskRead) -> Dict[str, Any]:
    """
    `task.args` MUST contain:

        {
            "action": "local-add" | "local-get" | "local-remove"
                    | "remote-add" | "remote-get" | "remote-remove",
            # corresponding argument blocks below …
        }
    """
    args: Dict[str, Any] = task.args or {}
    action: str | None = args.get("action")

    # ───── local operations ───────────────────────────────────────────
    if action == "local-add":
        recipients = [Path(p).expanduser() for p in args.get("recipients", [])]
        secrets_core.add_local_secret(args["name"], args["value"], recipients)
        return {"ok": True}

    if action == "local-get":
        return {"secret": secrets_core.get_local_secret(args["name"])}

    if action == "local-remove":
        secrets_core.remove_local_secret(args["name"])
        return {"ok": True}

    # ───── remote (gateway) operations ────────────────────────────────
    gw_url = args.get("gateway_url", secrets_core.DEFAULT_GATEWAY)
    pool = args.get("pool", "default")

    if action == "remote-add":
        recipients = [Path(p).expanduser() for p in args.get("recipient", [])]
        return secrets_core.add_remote_secret(
            secret_id=args["secret_id"],
            value=args["value"],
            gateway_url=gw_url,
            version=int(args.get("version", 0)),
            recipients=recipients,
            pool=pool,
        )

    if action == "remote-get":
        secret_val = secrets_core.get_remote_secret(
            secret_id=args["secret_id"],
            gateway_url=gw_url,
            pool=pool,
        )
        return {"secret": secret_val}

    if action == "remote-remove":
        return secrets_core.remove_remote_secret(
            secret_id=args["secret_id"],
            gateway_url=gw_url,
            version=args.get("version"),
            pool=pool,
        )

    # ───── unknown action ─────────────────────────────────────────────
    raise ValueError(f"Unknown secret-management action '{action}'")
