from __future__ import annotations

import base64, hashlib
from datetime import datetime, timezone

from fastapi import HTTPException

from tigrbl_acme_ca.tables.nonces import Nonce
from tigrbl_acme_ca.tables.challenges import Challenge
from tigrbl_acme_ca.tables.authorizations import Authorization
from tigrbl_acme_ca.tables.orders import Order

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

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

async def validate_challenge_task(ctx, *, challenge_id: str) -> dict:
    read_by_id = _h(ctx, "table.read.by_id")
    read_list = _h(ctx, "table.read.list")
    update = _h(ctx, "table.update")

    ch = await read_by_id(table=Challenge, id=challenge_id)
    if not ch:
        raise HTTPException(status_code=404, detail="challenge_not_found")

    authz = await read_by_id(table=Authorization, id=_field(ch, "authorization_id"))
    order = await read_by_id(table=Order, id=_field(authz, "order_id"))

    from tigrbl_acme_ca.tables.accounts import Account
    acct = await read_by_id(table=Account, id=_field(order, "account_id"))

    domain = _field(authz, "identifier")
    token = _field(ch, "token")
    jwk_thumbprint = _field(acct, "key_thumbprint")
    key_auth = f"{token}.{jwk_thumbprint}"

    ok = False
    if _field(ch, "type") == "dns-01":
        resolver = ctx.get("dns_resolver")
        if resolver is None:
            raise HTTPException(status_code=500, detail="dns_resolver_unavailable")
        name = f"_acme-challenge.{domain.rstrip('.')}"
        answers = await resolver.txt_lookup(name)
        expected = _b64url(hashlib.sha256(key_auth.encode("utf-8")).digest())
        candidates = {a.strip().strip('"') for a in (answers or [])}
        ok = expected in candidates
    elif _field(ch, "type") == "http-01":
        http = ctx.get("http_client")
        if http is None:
            raise HTTPException(status_code=500, detail="http_client_unavailable")
        url = f"http://{domain}/.well-known/acme-challenge/{token}"
        status, body = await http.get(url)
        ok = (status == 200 and (body or "").strip() == key_auth)
    else:
        raise HTTPException(status_code=400, detail="unsupported_challenge_type")

    if ok:
        await update(table=Challenge, id=challenge_id, values={"status": "valid", "validated_at": datetime.now(timezone.utc)})
        await update(table=Authorization, id=_id(authz), values={"status": "valid"})
        all_authzs = await read_list(table=Authorization, where={"order_id": _id(order)})
        if all_authzs and all((_field(a, "status") == "valid") for a in all_authzs):
            await update(table=Order, id=_id(order), values={"status": "ready"})
    else:
        await update(table=Challenge, id=challenge_id, values={"status": "invalid"})
        await update(table=Authorization, id=_id(authz), values={"status": "invalid"})

    return {"challenge_id": str(challenge_id), "status": "valid" if ok else "invalid"}

async def sweep_expired_nonces_task(ctx) -> int:
    delete = _h(ctx, "table.delete.where")
    now = datetime.now(timezone.utc)
    return await delete(table=Nonce, where={"expires_at__lte": now})

async def sweep_expired_authzs_orders_task(ctx) -> dict:
    read_list = _h(ctx, "table.read.list")
    update = _h(ctx, "table.update")

    now = datetime.now(timezone.utc)

    cnt_authz = 0
    authzs = await read_list(table=Authorization, where={"expires_at__lte": now})
    for a in authzs or []:
        if _field(a, "status") not in ("valid", "invalid"):
            await update(table=Authorization, id=_id(a), values={"status": "expired"})
            cnt_authz += 1

    cnt_orders = 0
    orders = await read_list(table=Order, where={"expires_at__lte": now})
    for o in orders or []:
        if _field(o, "status") not in ("valid", "invalid"):
            await update(table=Order, id=_id(o), values={"status": "invalid"})
            cnt_orders += 1

    return {"authzs": cnt_authz, "orders": cnt_orders}
