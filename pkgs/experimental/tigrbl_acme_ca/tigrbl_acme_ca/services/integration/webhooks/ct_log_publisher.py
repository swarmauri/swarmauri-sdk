from __future__ import annotations

from tigrbl.hook import hook_ctx
from tigrbl_acme_ca.tables.certificates import Certificate

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

@hook_ctx(ops=("finalize",), phase="POST_COMMIT")
async def _publish_to_ct(cls, ctx):
    ct = ctx.get("ct_client")
    if not ct:
        return
    order = ctx.get("result")
    if not order:
        return
    cert_id = _field(order, "certificate_id")
    if not cert_id:
        return
    read_by_id = _h(ctx, "table.read.by_id")
    cert = await read_by_id(table=Certificate, id=cert_id)
    if not cert:
        return
    try:
        await ct.submit_cert(_field(cert, "pem") or "")
    except Exception:
        pass
