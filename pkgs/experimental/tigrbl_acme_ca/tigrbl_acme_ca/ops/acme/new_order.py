from __future__ import annotations
from typing import Any, Dict, Sequence
from datetime import datetime, timedelta, timezone
import secrets

from fastapi import HTTPException
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

def _token() -> str:
    return secrets.token_urlsafe(24).rstrip("=")

async def new_order(ctx) -> Dict[str, Any]:
    p = ctx.get("payload") or {}
    account_id = p.get("account_id")
    identifiers: Sequence[str] = p.get("identifiers") or []
    if not account_id:
        raise HTTPException(status_code=400, detail="missing_account_id")
    if not identifiers:
        raise HTTPException(status_code=400, detail="identifiers_required")

    create = _h(ctx, "table.create")
    read_by_id = _h(ctx, "table.read.by_id")

    norm_ids = [i.strip().lower() for i in identifiers if i and i.strip()]
    now = datetime.now(timezone.utc)
    order = await create(table=Order, values={
        "account_id": account_id,
        "status": "pending",
        "identifiers": norm_ids,
        "expires_at": now + timedelta(seconds=_ORDER_TTL_SECONDS),
        "csr_der_b64": None,
        "certificate_id": None,
    })
    order_id = _id(order)
    order_obj = await read_by_id(table=Order, id=order_id)

    for name in norm_ids:
        is_wild = name.startswith("*.")
        authz = await create(table=Authorization, values={
            "order_id": order_id,
            "identifier": name,
            "status": "pending",
            "expires_at": _field(order_obj, "expires_at"),
            "wildcard": is_wild,
        })
        authz_id = _id(authz)
        if is_wild:
            await create(table=Challenge, values={"authorization_id": authz_id, "type": "dns-01", "status": "pending", "token": _token(), "validated_at": None})
        else:
            for ctype in ("http-01", "dns-01"):
                await create(table=Challenge, values={"authorization_id": authz_id, "type": ctype, "status": "pending", "token": _token(), "validated_at": None})

    return order
