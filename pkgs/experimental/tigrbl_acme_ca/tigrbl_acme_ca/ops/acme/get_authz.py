from __future__ import annotations
from fastapi import HTTPException
from tigrbl_acme_ca.tables.authorizations import Authorization


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


async def get_authorization(ctx, authorization_id: str):
    read_by_id = _h(ctx, "table.read.by_id")
    authz = await read_by_id(table=Authorization, id=authorization_id)
    if not authz:
        raise HTTPException(status_code=404, detail="authorization_not_found")
    return authz
