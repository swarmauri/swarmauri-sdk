from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from tigrbl.hook import hook_ctx

from tigrbl_acme_ca.tables.audit_events import AuditEvent
from tigrbl_acme_ca.services.audit.redact import redact_payload

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


def _actor_from_ctx(ctx) -> Optional[str]:
    return ctx.get("actor_account_id")


@hook_ctx(ops=("new_account",), phase="POST_COMMIT")
async def _audit_account_created(cls, ctx):
    acct = ctx.get("result")
    if not acct:
        return
    create = _h(ctx, "table.create")
    await create(
        table=AuditEvent,
        values={
            "event_type": "account.created",
            "actor_account_id": _actor_from_ctx(ctx),
            "object_type": "account",
            "object_id": _id(acct),
            "payload": redact_payload(ctx.get("payload")),
            "at": datetime.now(timezone.utc),
        },
    )


@hook_ctx(ops=("new_order",), phase="POST_COMMIT")
async def _audit_order_created(cls, ctx):
    order = ctx.get("result")
    if not order:
        return
    create = _h(ctx, "table.create")
    await create(
        table=AuditEvent,
        values={
            "event_type": "order.created",
            "actor_account_id": _actor_from_ctx(ctx),
            "object_type": "order",
            "object_id": _id(order),
            "payload": redact_payload(ctx.get("payload")),
            "at": datetime.now(timezone.utc),
        },
    )


@hook_ctx(ops=("finalize",), phase="POST_COMMIT")
async def _audit_certificate_issued(cls, ctx):
    order = ctx.get("result")
    if not order:
        return
    create = _h(ctx, "table.create")
    await create(
        table=AuditEvent,
        values={
            "event_type": "certificate.issued",
            "actor_account_id": _actor_from_ctx(ctx),
            "object_type": "order",
            "object_id": _id(order),
            "payload": {"certificate_id": _field(order, "certificate_id")},
            "at": datetime.now(timezone.utc),
        },
    )


@hook_ctx(ops=("revoke_cert",), phase="POST_COMMIT")
async def _audit_certificate_revoked(cls, ctx):
    rev = ctx.get("result")
    if not rev:
        return
    create = _h(ctx, "table.create")
    await create(
        table=AuditEvent,
        values={
            "event_type": "certificate.revoked",
            "actor_account_id": _actor_from_ctx(ctx),
            "object_type": "certificate",
            "object_id": _field(rev, "certificate_id"),
            "payload": redact_payload(ctx.get("payload")),
            "at": datetime.now(timezone.utc),
        },
    )
