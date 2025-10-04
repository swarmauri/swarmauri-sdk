from __future__ import annotations

import base64, secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from tigrbl_acme_ca.tables.orders import Order
from tigrbl_acme_ca.tables.authorizations import Authorization
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

def _b64url_to_bytes(data: str) -> bytes:
    pad = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)

async def ensure_certificate_task(ctx, *, order_id: str) -> dict:
    read_by_id = _h(ctx, "table.read.by_id")
    read_list = _h(ctx, "table.read.list")
    update = _h(ctx, "table.update")
    create = _h(ctx, "table.create")

    order = await read_by_id(table=Order, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order_not_found")

    if _field(order, "certificate_id"):
        return {"order_id": order_id, "status": _field(order, "status"), "certificate_id": str(_field(order, "certificate_id"))}

    if _field(order, "status") not in ("ready", "processing"):
        raise HTTPException(status_code=409, detail="order_not_in_processing")

    authzs = await read_list(table=Authorization, where={"order_id": order_id})
    if not authzs or any(_field(a, "status") != "valid" for a in authzs):
        raise HTTPException(status_code=409, detail="authorizations_not_all_valid")

    csr_b64 = _field(order, "csr_der_b64")
    if not csr_b64:
        raise HTTPException(status_code=400, detail="missing_csr")

    csr_der = _b64url_to_bytes(csr_b64)
    sans = list(_field(order, "identifiers") or [])

    engine = ctx.get("signing_engine")
    now = datetime.now(timezone.utc)
    not_before = now
    not_after = now + timedelta(days=int((ctx.get("config") or {}).get("acme.validity_days", 90)))

    if engine is not None and hasattr(engine, "issue_certificate"):
        issued = await engine.issue_certificate(csr_der=csr_der, sans=sans)
        pem = issued.get("pem")
        serial_hex = issued.get("serial_hex") or secrets.token_hex(16)
        nb = issued.get("not_before") or not_before
        na = issued.get("not_after") or not_after
    else:
        pem = "-----BEGIN CERTIFICATE-----\nMIIF...==\n-----END CERTIFICATE-----\n"
        serial_hex = secrets.token_hex(16)
        nb, na = not_before, not_after

    cert = await create(table=Certificate, values={"account_id": _field(order, "account_id"), "order_id": order_id, "serial_hex": serial_hex, "not_before": nb, "not_after": na, "pem": pem})
    await update(table=Order, id=order_id, values={"certificate_id": _id(cert), "status": "valid"})

    ct = ctx.get("ct_client")
    if ct:
        try:
            await ct.submit_cert(pem)
        except Exception:
            pass

    return {"order_id": order_id, "certificate_id": str(_id(cert))}

async def publish_ct_for_certificate_task(ctx, *, certificate_id: str) -> dict:
    read_by_id = _h(ctx, "table.read.by_id")

    from tigrbl_acme_ca.tables.certificates import Certificate
    cert = await read_by_id(table=Certificate, id=certificate_id)
    if not cert:
        raise HTTPException(status_code=404, detail="certificate_not_found")

    ct = ctx.get("ct_client")
    if not ct:
        return {"certificate_id": certificate_id, "published": False}

    try:
        await ct.submit_cert(_field(cert, "pem") or "")
        return {"certificate_id": certificate_id, "published": True}
    except Exception:
        return {"certificate_id": certificate_id, "published": False}
