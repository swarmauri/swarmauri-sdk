"""Async entry point for key management tasks."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from peagen.core import keys_core
from peagen.transport.jsonrpc_schemas.task import SubmitParams, SubmitResult


async def keys_handler(task: SubmitParams) -> SubmitResult:
    """Handle key management actions."""
    payload = task.payload
    action = payload.get("action")
    args: Dict[str, Any] = payload.get("args", {})

    if action == "create":
        return keys_core.create_keypair(
            key_dir=Path(args.get("key_dir")) if args.get("key_dir") else None,
            passphrase=args.get("passphrase"),
        )

    if action == "upload":
        return keys_core.upload_public_key(
            key_dir=Path(args.get("key_dir")) if args.get("key_dir") else None,
            gateway_url=args.get("gateway_url", keys_core.DEFAULT_GATEWAY),
        )

    if action == "remove":
        return keys_core.remove_public_key(
            args["fingerprint"],
            gateway_url=args.get("gateway_url", keys_core.DEFAULT_GATEWAY),
        )

    if action == "fetch-server":
        return keys_core.fetch_server_keys(
            gateway_url=args.get("gateway_url", keys_core.DEFAULT_GATEWAY)
        )

    raise ValueError(f"Unknown action '{action}'")
