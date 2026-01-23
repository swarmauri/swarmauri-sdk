from __future__ import annotations
import base64
import hashlib
from datetime import datetime, timezone

from fastapi import HTTPException

from tigrbl_acme_ca.tables.challenges import Challenge
from tigrbl_acme_ca.tables.authorizations import Authorization
from tigrbl_acme_ca.tables.orders import Order
from tigrbl_acme_ca.tables.accounts import Account


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


async def post_challenge(ctx, challenge_id: str | None = None):
    read_by_id = _h(ctx, "table.read.by_id")
    read_list = _h(ctx, "table.read.list")
    update = _h(ctx, "table.update")

    if challenge_id is None:
        challenge_id = (ctx.get("path_params") or {}).get("id")
    if not challenge_id:
        raise HTTPException(status_code=400, detail="missing_challenge_id")

    ch = await read_by_id(table=Challenge, id=challenge_id)
    if not ch:
        raise HTTPException(status_code=404, detail="challenge_not_found")

    authz = await read_by_id(table=Authorization, id=_field(ch, "authorization_id"))
    order = await read_by_id(table=Order, id=_field(authz, "order_id"))
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
        expected = (
            base64.urlsafe_b64encode(hashlib.sha256(key_auth.encode("utf-8")).digest())
            .rstrip(b"=")
            .decode("ascii")
        )
        candidates = {a.strip().strip('"') for a in (answers or [])}
        ok = expected in candidates
    elif _field(ch, "type") == "http-01":
        http = ctx.get("http_client")
        if http is None:
            raise HTTPException(status_code=500, detail="http_client_unavailable")
        url = f"http://{domain}/.well-known/acme-challenge/{token}"
        status, body = await http.get(url)
        ok = status == 200 and (body or "").strip() == key_auth
    else:
        raise HTTPException(status_code=400, detail="unsupported_challenge_type")

    if ok:
        await update(
            table=Challenge,
            id=challenge_id,
            values={"status": "valid", "validated_at": datetime.now(timezone.utc)},
        )
        await update(table=Authorization, id=_id(authz), values={"status": "valid"})
        authzs = await read_list(table=Authorization, where={"order_id": _id(order)})
        if authzs and all((_field(a, "status") == "valid") for a in authzs):
            await update(table=Order, id=_id(order), values={"status": "ready"})
    else:
        await update(table=Challenge, id=challenge_id, values={"status": "invalid"})
        await update(table=Authorization, id=_id(authz), values={"status": "invalid"})

    return {"challenge_id": str(challenge_id), "status": "valid" if ok else "invalid"}
