from __future__ import annotations

from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import select

from tigrbl_acme_ca.tables.revocations import Revocation
from tigrbl_acme_ca.tables.certificates import Certificate

async def rebuild_crl_task(ctx) -> dict:
    """Trigger CRL rebuild via ctx-injected CRL builder/publisher."""
    builder = ctx.get("crl_builder")
    publisher = ctx.get("crl_publisher")
    if not builder:
        return {"reissued": False}
    try:
        crl_pem = await builder.build_crl()
        if publisher:
            try:
                await publisher.publish(crl_pem)
            except Exception:
                pass
        return {"reissued": True}
    except Exception:
        return {"reissued": False}

async def ocsp_refresh_task(ctx, *, certificate_ids: list[str] | None = None) -> dict:
    responder = ctx.get("ocsp_responder")
    if not responder:
        return {"refreshed": 0}
    refreshed = 0
    # If no cert list given, refresh recently revoked certs
    if not certificate_ids:
        db = ctx.get("db")
        if db is None:
            return {"refreshed": 0}
        res = await db.execute(select(Revocation))
        for r in res.scalars().all():
            try:
                await responder.refresh(certificate_id=str(r.certificate_id))
                refreshed += 1
            except Exception:
                pass
        return {"refreshed": refreshed}
    else:
        for cid in certificate_ids:
            try:
                await responder.refresh(certificate_id=cid)
                refreshed += 1
            except Exception:
                pass
        return {"refreshed": refreshed}
