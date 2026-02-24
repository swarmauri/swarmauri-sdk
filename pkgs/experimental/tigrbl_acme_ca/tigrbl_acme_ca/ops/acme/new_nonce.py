from __future__ import annotations
from typing import Any, Dict
from datetime import datetime, timedelta, timezone
import base64
import secrets

from fastapi import HTTPException
from tigrbl_acme_ca.tables.nonces import Nonce


def _h(ctx, name: str):
    handlers = ctx.get("handlers") or {}
    fn = handlers.get(name)
    if not fn:
        raise HTTPException(status_code=500, detail=f"handler_unavailable:{name}")
    return fn


def _id(obj):
    return obj.get("id") if isinstance(obj, dict) else getattr(obj, "id", None)


def _field(obj, name: str):
    return obj.get(name) if isinstance(obj, dict) else getattr(obj, name, None)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


async def new_nonce(ctx) -> Dict[str, Any]:
    create = _h(ctx, "table.create")
    ttl = int((ctx.get("config") or {}).get("acme.nonce_ttl_seconds", 300))
    value = _b64url(secrets.token_bytes(24))
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
    await create(
        table=Nonce, values={"value": value, "used": False, "expires_at": expires_at}
    )
    try:
        headers = ctx.response_headers()
        headers["Replay-Nonce"] = value
    except Exception:
        pass
    return {}
