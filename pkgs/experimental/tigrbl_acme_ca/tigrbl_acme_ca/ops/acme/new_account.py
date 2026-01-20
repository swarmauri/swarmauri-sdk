from __future__ import annotations
from typing import Any, Dict, Sequence
from datetime import datetime, timezone

from fastapi import HTTPException
from tigrbl_acme_ca.tables.accounts import Account
from tigrbl_acme_ca.tables.tos_agreements import TosAgreement


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


async def new_account(ctx) -> Dict[str, Any]:
    p = ctx.get("payload") or {}
    key_thumbprint: str = (p.get("key_thumbprint") or "").strip()
    contacts: Sequence[str] = p.get("contacts") or []
    external_binding = p.get("external_binding")
    terms_agreed: bool = bool(p.get("terms_of_service_agreed", False))

    if not key_thumbprint:
        raise HTTPException(status_code=400, detail="missing_key_thumbprint")
    if not terms_agreed:
        raise HTTPException(status_code=400, detail="terms_of_service_not_accepted")

    read_one = _h(ctx, "table.read.one")
    create = _h(ctx, "table.create")

    existing = await read_one(table=Account, where={"key_thumbprint": key_thumbprint})
    if existing:
        return existing

    now = datetime.now(timezone.utc)
    acct = await create(
        table=Account,
        values={
            "key_thumbprint": key_thumbprint,
            "status": "valid",
            "contacts": list(contacts),
            "external_binding": external_binding,
            "created_at": now,
            "deactivated_at": None,
        },
    )
    await create(
        table=TosAgreement, values={"account_id": _id(acct), "agreed": True, "at": now}
    )
    return acct
