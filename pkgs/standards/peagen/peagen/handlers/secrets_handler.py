"""Async entry point for secret management."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from peagen.core import secrets_core
from peagen.models.tasks import Task


async def secrets_handler(task: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Dispatch secret management actions."""
    payload = task.get("payload", {})
    action = payload.get("action")
    args: Dict[str, Any] = payload.get("args", {})

    if action == "local-add":
        recipients = [Path(p) for p in args.get("recipients", [])]
        secrets_core.add_local_secret(args["name"], args["value"], recipients)
        return {"ok": True}

    if action == "local-get":
        return {"secret": secrets_core.get_local_secret(args["name"])}

    if action == "local-remove":
        secrets_core.remove_local_secret(args["name"])
        return {"ok": True}

    if action == "remote-add":
        recipients = [Path(p) for p in args.get("recipient", [])]
        return secrets_core.add_remote_secret(
            args["secret_id"],
            args["value"],
            gateway_url=args.get("gateway_url", secrets_core.DEFAULT_GATEWAY),
            version=int(args.get("version", 0)),
            recipients=recipients,
            pool=args.get("pool", "default"),
        )

    if action == "remote-get":
        secret = secrets_core.get_remote_secret(
            args["secret_id"],
            gateway_url=args.get("gateway_url", secrets_core.DEFAULT_GATEWAY),
            pool=args.get("pool", "default"),
        )
        return {"secret": secret}

    if action == "remote-remove":
        return secrets_core.remove_remote_secret(
            args["secret_id"],
            gateway_url=args.get("gateway_url", secrets_core.DEFAULT_GATEWAY),
            version=args.get("version"),
            pool=args.get("pool", "default"),
        )

    raise ValueError(f"Unknown action '{action}'")
