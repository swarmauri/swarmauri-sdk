from __future__ import annotations
from typing import Any, Dict

from fastapi import HTTPException
from tigrbl_acme_ca.tables.accounts import Account

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

async def key_change(ctx) -> Dict[str, Any]:
    p = ctx.get("payload") or {}
    account_id = p.get("account_id")
    new_key_thumbprint = (p.get("new_key_thumbprint") or "").strip()
    if not account_id or not new_key_thumbprint:
        raise HTTPException(status_code=400, detail="missing_parameters")

    read_by_id = _h(ctx, "table.read.by_id")
    update = _h(ctx, "table.update")

    acct = await read_by_id(table=Account, id=account_id)
    if not acct:
        raise HTTPException(status_code=404, detail="account_not_found")

    if _field(acct, "key_thumbprint") != new_key_thumbprint:
        await update(table=Account, id=account_id, values={"key_thumbprint": new_key_thumbprint})

    return {"account_id": str(account_id), "key_thumbprint": new_key_thumbprint}
