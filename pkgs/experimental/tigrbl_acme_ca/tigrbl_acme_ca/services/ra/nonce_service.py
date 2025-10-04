from __future__ import annotations

import base64
import os
from datetime import datetime, timedelta, timezone

from tigrbl.op import op_ctx
from tigrbl.hook import hook_ctx

from tigrbl_acme_ca.tables.nonces import Nonce


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


@op_ctx(
    alias="new_nonce",
    target="create",
    arity="collection",
    persist="default",
)
async def new_nonce(cls, ctx):
    ttl = int(os.getenv("ACME_NONCE_TTL_SECONDS", "300"))
    value = _b64url(os.urandom(24))
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
    ctx["payload"] = {"value": value, "used": False, "expires_at": expires_at}


@hook_ctx(ops=("new_nonce",), phase="POST_RESPONSE")
async def _attach_replay_nonce_header(cls, ctx):
    res = ctx.get("result")
    if not res:
        return
    try:
        headers = ctx.response_headers()
        headers["Replay-Nonce"] = getattr(res, "value", None) or res.get("value")
    except Exception:
        pass


setattr(Nonce, "new_nonce", new_nonce)
setattr(Nonce, "_attach_replay_nonce_header", _attach_replay_nonce_header)
