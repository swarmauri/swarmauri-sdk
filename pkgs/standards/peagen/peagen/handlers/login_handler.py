"""Async entry point for login operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from peagen.core.login_core import login
from peagen.models import Task
from . import ensure_task


async def login_handler(task: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Handle a login task."""
    task = ensure_task(task)
    payload = task.payload
    args: Dict[str, Any] = payload.get("args", {})
    key_dir = args.get("key_dir")
    passphrase: Optional[str] = args.get("passphrase")
    gateway_url = args.get("gateway_url", "http://localhost:8000/rpc")
    result = login(
        key_dir=Path(key_dir) if key_dir else None,
        passphrase=passphrase,
        gateway_url=gateway_url,
    )
    return result
