# peagen/handlers/keys_handler.py
"""
Async entry-point for key-management tasks.

Input : TaskRead  (AutoAPI schema for the Task table)
Output: dict      – whatever the underlying keys_core helper returns
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from autoapi.v2 import AutoAPI
from peagen.orm import Task

from peagen.core import keys_core

# ─────────────────────────── AutoAPI schema ───────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")  # incoming model


# ─────────────────────────── main coroutine  ──────────────────────────
async def keys_handler(task: TaskRead) -> Dict[str, Any]:
    """
    Handle key-management *actions* sent through an AutoAPI Task.

    Expected structure
    ------------------
    task.payload == {
        "action": "create" | "upload" | "remove" | "fetch-server",
        "args":   { ... }
    }
    """
    payload: Dict[str, Any] = task.payload or {}
    action: str | None = payload.get("action")
    args: Dict[str, Any] = payload.get("args", {})

    if action == "create":
        return keys_core.create_keypair(
            key_dir=Path(args["key_dir"]).expanduser() if args.get("key_dir") else None,
            passphrase=args.get("passphrase"),
        )

    if action == "upload":
        return keys_core.upload_public_key(
            key_dir=Path(args["key_dir"]).expanduser() if args.get("key_dir") else None,
            gateway_url=args.get("gateway_url", keys_core.DEFAULT_GATEWAY),
        )

    if action == "remove":
        return keys_core.remove_public_key(
            fingerprint=args["fingerprint"],
            gateway_url=args.get("gateway_url", keys_core.DEFAULT_GATEWAY),
        )

    if action == "fetch-server":
        return keys_core.fetch_server_keys(
            gateway_url=args.get("gateway_url", keys_core.DEFAULT_GATEWAY),
        )

    raise ValueError(f"Unknown key-management action '{action}'")
