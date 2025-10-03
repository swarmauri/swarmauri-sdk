from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence, Optional

from fastapi import HTTPException
from tigrbl.op import op_ctx
from tigrbl.hook import hook_ctx
try:
    from tigrbl.config.constants import CTX_SKIP_PERSIST_FLAG
except Exception:
    CTX_SKIP_PERSIST_FLAG = "_tigrbl_skip_persist_"  # fallback

from tigrbl_acme_ca.tables.accounts import Account
from tigrbl_acme_ca.tables.tos_agreements import TosAgreement

from fastapi import HTTPException

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
    alias="new_account",
    target="create",
    arity="collection",
    persist="default",
)
async def new_account(cls, ctx):
    p = ctx.get("payload") or {}
    key_thumbprint: str = (p.get("key_thumbprint") or "").strip()
    contacts: Sequence[str] = p.get("contacts") or []
    external_binding: Optional[str] = p.get("external_binding")
    terms_agreed: bool = bool(p.get("terms_of_service_agreed", False))

    if not key_thumbprint:
        raise HTTPException(status_code=400, detail="missing_key_thumbprint")
    if not terms_agreed:
        raise HTTPException(status_code=400, detail="terms_of_service_not_accepted")

    now = datetime.now(timezone.utc)
    ctx["payload"] = {
        "key_thumbprint": key_thumbprint,
        "status": "valid",
        "contacts": list(contacts),
        "external_binding": external_binding,
        "created_at": now,
        "deactivated_at": None,
    }


@hook_ctx(ops=("new_account",), phase="PRE_HANDLER")
async def _idempotent_by_thumbprint(cls, ctx):
    p = ctx.get("payload") or {}
    tprint = p.get("key_thumbprint")
    if not tprint:
        return
    read_one = _h(ctx, "table.read.one")
    existing = await read_one(table=Account, where={"key_thumbprint": tprint})
    if existing:
        ctx[CTX_SKIP_PERSIST_FLAG] = True
        ctx["result"] = existing
        ctx.setdefault("temp", {})["__existing_account__"] = True


@hook_ctx(ops=("new_account",), phase="POST_COMMIT")
async def _record_tos(cls, ctx):
    if ctx.get("temp", {}).get("__existing_account__"):
        return
    obj = ctx.get("result")
    if not obj:
        return
    create = _h(ctx, "table.create")
    await create(table=TosAgreement, values={
        "account_id": _id(obj),
        "agreed": True,
        "at": datetime.now(timezone.utc),
    })

setattr(Account, "new_account", new_account)
setattr(Account, "_idempotent_by_thumbprint", _idempotent_by_thumbprint)
setattr(Account, "_record_tos", _record_tos)
