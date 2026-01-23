from __future__ import annotations
from typing import Any, Dict
from datetime import datetime, timezone

from fastapi import HTTPException
from tigrbl_acme_ca.tables.revocations import Revocation
from tigrbl_acme_ca.tables.certificates import Certificate


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


async def revoke(ctx) -> Dict[str, Any]:
    p = ctx.get("payload") or {}
    certificate_id = p.get("certificate_id")
    reason = p.get("reason")

    read_one = _h(ctx, "table.read.one")
    create = _h(ctx, "table.create")

    if not certificate_id:
        serial_hex = p.get("serial_hex")
        if not serial_hex:
            raise HTTPException(
                status_code=400, detail="missing_certificate_id_or_serial"
            )
        cert = await read_one(table=Certificate, where={"serial_hex": serial_hex})
        if not cert:
            raise HTTPException(status_code=404, detail="certificate_not_found")
        certificate_id = _id(cert)

    existing = await read_one(
        table=Revocation, where={"certificate_id": certificate_id}
    )
    if existing:
        return {
            "revocation_id": str(_id(existing)),
            "certificate_id": str(certificate_id),
        }

    rec = await create(
        table=Revocation,
        values={
            "certificate_id": certificate_id,
            "reason": reason,
            "revoked_at": datetime.now(timezone.utc),
        },
    )
    return {"certificate_id": str(certificate_id), "revocation_id": str(_id(rec))}
