from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from tigrbl.op import op_ctx
from tigrbl.hook import hook_ctx

from tigrbl_acme_ca.tables.challenges import Challenge
from tigrbl_acme_ca.tables.authorizations import Authorization
from tigrbl_acme_ca.tables.orders import Order
from tigrbl_acme_ca.tables.accounts import Account

from tigrbl_acme_ca.services.va.dns01_validator import validate_dns01
from tigrbl_acme_ca.services.va.http01_validator import validate_http01


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
    alias="submit_challenge",
    target="update",
    arity="member",
    persist="default",
)
async def submit_challenge(cls, ctx):
    ctx.setdefault("payload", {})
    ctx["payload"].update({"status": "processing"})


@hook_ctx(ops=("submit_challenge",), phase="POST_HANDLER")
async def _validate_and_mark(cls, ctx):
    read_by_id = _h(ctx, "table.read.by_id")
    read_list = _h(ctx, "table.read.list")
    update = _h(ctx, "table.update")

    ch = ctx.get("result")
    if not ch:
        return

    ch_id = _id(ch)
    ch_obj = await read_by_id(table=Challenge, id=ch_id)

    authz = await read_by_id(table=Authorization, id=_field(ch_obj, "authorization_id"))
    order = await read_by_id(table=Order, id=_field(authz, "order_id"))
    acct = await read_by_id(table=Account, id=_field(order, "account_id"))

    domain = _field(authz, "identifier")
    token = _field(ch_obj, "token")
    jwk_thumbprint = _field(acct, "key_thumbprint")
    key_auth = f"{token}.{jwk_thumbprint}"

    ok = False
    if _field(ch_obj, "type") == "dns-01":
        ok = await validate_dns01(ctx, domain, token, jwk_thumbprint)
    elif _field(ch_obj, "type") == "http-01":
        ok = await validate_http01(ctx, domain, token, key_auth)
    else:
        raise HTTPException(status_code=400, detail="unsupported_challenge_type")

    if ok:
        await update(
            table=Challenge,
            id=ch_id,
            values={"status": "valid", "validated_at": datetime.now(timezone.utc)},
        )
        await update(table=Authorization, id=_id(authz), values={"status": "valid"})
        authzs = await read_list(table=Authorization, where={"order_id": _id(order)})
        if authzs and all((_field(a, "status") == "valid") for a in authzs):
            await update(table=Order, id=_id(order), values={"status": "ready"})
    else:
        await update(table=Challenge, id=ch_id, values={"status": "invalid"})
        await update(table=Authorization, id=_id(authz), values={"status": "invalid"})


setattr(Challenge, "submit_challenge", submit_challenge)
setattr(Challenge, "_validate_and_mark", _validate_and_mark)
