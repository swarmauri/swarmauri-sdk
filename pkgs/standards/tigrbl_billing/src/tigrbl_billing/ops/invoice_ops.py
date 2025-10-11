from __future__ import annotations
from typing import Optional, Sequence, Mapping
from tigrbl import op_ctx
from tigrbl_billing.tables.invoice import Invoice, InvoiceStatus


@op_ctx(
    alias="finalize", target="custom", arity="member", bind=Invoice, persist="default"
)
async def finalize_invoice(
    *,
    invoice_id,
    line_items: Optional[Sequence[Mapping[str, object]]] = None,
    model=None,
    ctx=None,
    payload=None,
    spec=None,
) -> dict:
    # We cannot mutate line items here without DB access; instead, finalize metadata/status.
    ctx["path_params"] = {"invoice_id": invoice_id}
    body = {"status": InvoiceStatus.OPEN.name}
    if line_items is not None:
        body["line_items"] = list(
            line_items
        )  # handlers/schemas may map this to child ops
    ctx["payload"] = body
    return await model.handlers.update.handler(ctx)


@op_ctx(alias="void", target="custom", arity="member", bind=Invoice, persist="default")
async def void_invoice(*, invoice_id, model=None, ctx=None, **_):
    ctx["path_params"] = {"invoice_id": invoice_id}
    ctx["payload"] = {"status": InvoiceStatus.VOID.name}
    return await model.handlers.update.handler(ctx)


@op_ctx(
    alias="mark_uncollectible",
    target="custom",
    arity="member",
    bind=Invoice,
    persist="default",
)
async def mark_invoice_uncollectible(*, invoice_id, model=None, ctx=None, **_):
    ctx["path_params"] = {"invoice_id": invoice_id}
    ctx["payload"] = {"status": InvoiceStatus.UNCOLLECTIBLE.name}
    return await model.handlers.update.handler(ctx)
