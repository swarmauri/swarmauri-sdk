from __future__ import annotations
from tigrbl_acme_ca.tables.certificates import Certificate
from fastapi import HTTPException

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

async def get_certificate(ctx, certificate_id: str):
    read_by_id = _h(ctx, "table.read.by_id")
    cert = await read_by_id(table=Certificate, id=certificate_id)
    if not cert:
        raise HTTPException(status_code=404, detail="certificate_not_found")
    return {"pem": _field(cert, "pem"), "id": _id(cert)}
