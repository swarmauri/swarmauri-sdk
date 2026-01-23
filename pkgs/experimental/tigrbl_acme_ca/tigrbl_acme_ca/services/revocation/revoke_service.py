from __future__ import annotations

from datetime import datetime, timezone
from fastapi import HTTPException

from tigrbl.op import op_ctx
from tigrbl.hook import hook_ctx

try:
    from tigrbl.config.constants import CTX_SKIP_PERSIST_FLAG
except Exception:
    CTX_SKIP_PERSIST_FLAG = "_tigrbl_skip_persist_"

from tigrbl_acme_ca.tables.revocations import Revocation


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


@op_ctx(
    alias="revoke_cert",
    target="create",
    arity="collection",
    persist="default",
)
async def revoke_cert(cls, ctx):
    p = ctx.get("payload") or {}
    cert_id = p.get("certificate_id")
    if not cert_id:
        raise HTTPException(status_code=400, detail="missing_certificate_id")
    ctx["payload"] = {
        "certificate_id": cert_id,
        "reason": p.get("reason"),
        "revoked_at": datetime.now(timezone.utc),
    }


@hook_ctx(ops=("revoke_cert",), phase="PRE_HANDLER")
async def _idempotent_revocation(cls, ctx):
    p = ctx.get("payload") or {}
    cid = p.get("certificate_id")
    if not cid:
        return
    read_one = _h(ctx, "table.read.one")
    existing = await read_one(table=Revocation, where={"certificate_id": cid})
    if existing:
        ctx[CTX_SKIP_PERSIST_FLAG] = True
        ctx["result"] = existing


setattr(Revocation, "revoke_cert", revoke_cert)
setattr(Revocation, "_idempotent_revocation", _idempotent_revocation)
