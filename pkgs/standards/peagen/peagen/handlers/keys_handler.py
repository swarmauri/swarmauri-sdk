"""
peagen.handlers.keys_handler
────────────────────────────
Async entry-point for key-management tasks.

Input  : TaskRead  – AutoAPI schema for the Task ORM table
Output : dict      – passthrough result from peagen.core.keys_core helpers
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from autoapi.v2 import AutoAPI
from peagen.orm  import Task

from peagen.core import keys_core

# ───────────────────────── schema handle ──────────────────────────────
TaskRead = AutoAPI.get_schema(Task, "read")          # validated Pydantic model


# ───────────────────────── main coroutine ─────────────────────────────
async def keys_handler(task: TaskRead) -> Dict[str, Any]:
    """
    `task.args` MUST contain:

        {
            "action": "create" | "upload" | "remove" | "fetch-server",
            # create          → { "key_dir": "<dir>", "passphrase": "..." }
            # upload/remove   → { "key_dir": "<dir>", ...  gateway_url?: str }
            # fetch-server    → { "gateway_url": "<url>" }
            # remove          → { "fingerprint": "<fp>", ... }
        }
    """
    args: Dict[str, Any] = task.args or {}
    action: str | None   = args.get("action")

    if action == "create":
        return keys_core.create_keypair(
            key_dir   = Path(args.get("key_dir", "")).expanduser() if args.get("key_dir") else None,
            passphrase= args.get("passphrase"),
        )

    if action == "upload":
        return keys_core.upload_public_key(
            key_dir     = Path(args.get("key_dir", "")).expanduser() if args.get("key_dir") else None,
            gateway_url = args.get("gateway_url", keys_core.DEFAULT_GATEWAY),
        )

    if action == "remove":
        return keys_core.remove_public_key(
            fingerprint = args["fingerprint"],
            gateway_url = args.get("gateway_url", keys_core.DEFAULT_GATEWAY),
        )

    if action == "fetch-server":
        return keys_core.fetch_server_keys(
            gateway_url = args.get("gateway_url", keys_core.DEFAULT_GATEWAY),
        )

    raise ValueError(f"Unknown key-management action '{action}'")
