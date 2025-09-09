"""
Async entry-point for key-management tasks executed by workers / runners.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import anyio
from tigrbl.v3 import get_schema
from peagen.core import keys_core
from peagen.defaults import DEFAULT_GATEWAY
from peagen.orm import Task
from pydantic import BaseModel, Field, ValidationError


# ─────────────────────────── argument models ────────────────────────────
class _Base(BaseModel):
    action: str


class _Create(_Base):
    action: str = Field("create", json_schema_extra={"Literal": True})
    key_dir: Path | None = None
    passphrase: str | None = None


class _Upload(_Base):
    action: str = Field("upload", json_schema_extra={"Literal": True})
    key_dir: Path | None = None
    passphrase: str | None = None
    gateway_url: str = DEFAULT_GATEWAY


class _Remove(_Base):
    action: str = Field("remove", json_schema_extra={"Literal": True})
    fingerprint: str
    gateway_url: str = DEFAULT_GATEWAY


class _Fetch(_Base):
    action: str = Field("fetch-server", json_schema_extra={"Literal": True})
    gateway_url: str = DEFAULT_GATEWAY


_ArgsUnion = _Create | _Upload | _Remove | _Fetch

# schema alias so we don’t import Tigrbl in call-sites
TaskRead = get_schema(Task, "read")

# ───────────────────────────── dispatcher ───────────────────────────────
_ACTIONS: dict[str, callable] = {
    "create": lambda a: keys_core.create_keypair(a.key_dir, a.passphrase),
    "upload": lambda a: keys_core.upload_public_key(
        a.key_dir, a.passphrase, a.gateway_url
    ),
    "remove": lambda a: keys_core.remove_public_key(a.fingerprint, a.gateway_url),
    "fetch-server": lambda a: keys_core.fetch_server_keys(a.gateway_url),
}


# ──────────────────────────── entry-point ───────────────────────────────
async def keys_handler(task: TaskRead) -> Dict[str, Any]:  # noqa: D401
    try:
        args = _ArgsUnion.model_validate(task.args or {})
    except ValidationError as exc:
        raise ValueError(f"Invalid key-management arguments: {exc}") from exc

    # call sync helper inside a worker thread to avoid blocking the event-loop
    return await anyio.to_thread.run_sync(_ACTIONS[args.action], args)
