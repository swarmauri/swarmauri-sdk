from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from tigrbl.op import op_ctx
from tigrbl.hook import hook_ctx

try:
    from tigrbl.config.constants import CTX_SKIP_PERSIST_FLAG
except Exception:
    CTX_SKIP_PERSIST_FLAG = "_tigrbl_skip_persist_"

from tigrbl_acme_ca.tables.orders import Order
from tigrbl_acme_ca.tables.authorizations import Authorization
from tigrbl_acme_ca.tables.certificates import Certificate
from tigrbl_acme_ca.services.ca.csr_service import b64url_to_bytes
from tigrbl_acme_ca.services.ca.policy import (
    check_identifiers_allowed,
    check_csr_matches_identifiers,
)
from tigrbl_acme_ca.services.ca.chain_builder import build_chain


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


@op_ctx(
    alias="finalize",
    target="update",
    arity="member",
    persist="default",
)
async def finalize_order(cls, ctx):
    p = ctx.get("payload") or {}
    csr_b64 = p.get("csr") or p.get("csr_der_b64")
    if not csr_b64:
        raise HTTPException(status_code=400, detail="missing_csr")
    ctx.setdefault("payload", {})
    ctx["payload"].update(
        {
            "csr_der_b64": csr_b64,
            "status": "processing",
        }
    )


@hook_ctx(ops=("finalize",), phase="PRE_HANDLER")
async def _ensure_ready_and_valid_authzs(cls, ctx):
    read_by_id = _h(ctx, "table.read.by_id")
    read_list = _h(ctx, "table.read.list")

    order = ctx.get("instance")  # bound member
    if not order:
        raise HTTPException(status_code=500, detail="context_invalid")

    order_obj = await read_by_id(table=Order, id=_id(order))
    if _field(order_obj, "status") != "ready":
        raise HTTPException(status_code=409, detail="order_not_ready")

    authzs = await read_list(table=Authorization, where={"order_id": _id(order)})
    if not authzs or any(_field(a, "status") != "valid" for a in authzs):
        raise HTTPException(status_code=409, detail="authorizations_not_all_valid")


@hook_ctx(ops=("finalize",), phase="POST_HANDLER")
async def _issue_certificate_and_close_order(cls, ctx):
    read_by_id = _h(ctx, "table.read.by_id")
    update = _h(ctx, "table.update")
    create = _h(ctx, "table.create")

    order = ctx.get("result")
    if not order:
        return
    order_id = _id(order)
    order_obj = await read_by_id(table=Order, id=order_id)

    csr_b64 = _field(order_obj, "csr_der_b64")
    if not csr_b64:
        raise HTTPException(status_code=400, detail="missing_csr_after_update")

    csr_der = b64url_to_bytes(csr_b64)
    identifiers = list(_field(order_obj, "identifiers") or [])

    # Policy
    check_identifiers_allowed(identifiers)
    check_csr_matches_identifiers(csr_der, identifiers)

    engine = ctx.get("signing_engine")
    now = datetime.now(timezone.utc)
    not_before = now
    not_after = now + timedelta(days=90)

    if engine is not None and hasattr(engine, "issue_certificate"):
        issued = await engine.issue_certificate(csr_der=csr_der, sans=identifiers)
        pem = issued.get("pem")
        serial_hex = issued.get("serial_hex") or secrets.token_hex(16)
        nb = issued.get("not_before") or not_before
        na = issued.get("not_after") or not_after
    else:
        pem = "-----BEGIN CERTIFICATE-----\nMIIF...==\n-----END CERTIFICATE-----\n"
        serial_hex = secrets.token_hex(16)
        nb, na = not_before, not_after

    cert = await create(
        table=Certificate,
        values={
            "account_id": _field(order_obj, "account_id"),
            "order_id": order_id,
            "serial_hex": serial_hex,
            "not_before": nb,
            "not_after": na,
            "pem": pem,
        },
    )

    _ = build_chain(leaf_pem=pem)
    await update(
        table=Order,
        id=order_id,
        values={"certificate_id": _id(cert), "status": "valid"},
    )
