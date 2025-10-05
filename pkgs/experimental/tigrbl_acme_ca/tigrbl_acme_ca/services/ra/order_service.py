from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Sequence

from fastapi import HTTPException
from tigrbl.op import op_ctx
from tigrbl.hook import hook_ctx

from tigrbl_acme_ca.tables.orders import Order
from tigrbl_acme_ca.tables.authorizations import Authorization
from tigrbl_acme_ca.tables.challenges import Challenge

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

_ORDER_TTL_SECONDS = 7 * 24 * 3600

@op_ctx(
    alias="new_order",
    target="create",
    arity="collection",
    persist="default",
)
async def new_order(cls, ctx):
    p = ctx.get("payload") or {}
    account_id = p.get("account_id")
    identifiers: Sequence[str] = p.get("identifiers") or []
    if not account_id:
        raise HTTPException(status_code=400, detail="missing_account_id")
    if not identifiers:
        raise HTTPException(status_code=400, detail="identifiers_required")

    norm_ids = [i.strip().lower() for i in identifiers if i and i.strip()]
    now = datetime.now(timezone.utc)
    ctx["payload"] = {
        "account_id": account_id,
        "status": "pending",
        "identifiers": norm_ids,
        "expires_at": now + timedelta(seconds=_ORDER_TTL_SECONDS),
        "csr_der_b64": None,
        "certificate_id": None,
    }


@hook_ctx(ops=("new_order",), phase="POST_HANDLER")
async def _provision_authzs_and_challenges(cls, ctx):
    create = _h(ctx, "table.create")
    read_by_id = _h(ctx, "table.read.by_id")

    order = ctx.get("result")
    if not order:
        return

    order_id = _id(order)
    order_obj = await read_by_id(table=Order, id=order_id)
    identifiers = list(_field(order_obj, "identifiers") or [])
    expires_at = _field(order_obj, "expires_at")

    def _token() -> str:
        return secrets.token_urlsafe(24).rstrip("=")

    for name in identifiers:
        is_wild = name.startswith("*.")
        authz = await create(table=Authorization, values={
            "order_id": order_id,
            "identifier": name,
            "status": "pending",
            "expires_at": expires_at,
            "wildcard": is_wild,
        })
        authz_id = _id(authz)
        if is_wild:
            await create(table=Challenge, values={
                "authorization_id": authz_id,
                "type": "dns-01",
                "status": "pending",
                "token": _token(),
                "validated_at": None,
            })
        else:
            for ctype in ("http-01", "dns-01"):
                await create(table=Challenge, values={
                    "authorization_id": authz_id,
                    "type": ctype,
                    "status": "pending",
                    "token": _token(),
                    "validated_at": None,
                })

setattr(Order, "new_order", new_order)
setattr(Order, "_provision_authzs_and_challenges", _provision_authzs_and_challenges)
