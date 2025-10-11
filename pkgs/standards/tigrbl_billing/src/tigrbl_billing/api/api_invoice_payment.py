"""
API for a specific billing strategy, built with tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert use tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle ops are bound via @op_ctx(bind=...).
"""

from tigrbl import TigrblApp, op_ctx
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing.tables.invoice import Invoice
from tigrbl_billing.tables.invoice_line_item import InvoiceLineItem
from tigrbl_billing.tables.payment_intent import PaymentIntent
from tigrbl_billing.tables.refund import Refund
from tigrbl_billing.ops import (
    finalize_invoice,
    void_invoice,
    mark_invoice_uncollectible,
    capture_payment_intent,
    cancel_payment_intent,
)


@op_ctx(alias="finalize", target="custom", arity="collection", bind=Invoice)
def invoice__finalize(cls, ctx):
    return finalize_invoice(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="void", target="custom", arity="collection", bind=Invoice)
def invoice__void(cls, ctx):
    return void_invoice(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="mark_uncollectible", target="custom", arity="collection", bind=Invoice)
def invoice__mark_uncollectible(cls, ctx):
    return mark_invoice_uncollectible(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="capture", target="custom", arity="collection", bind=PaymentIntent)
def payment_intent__capture(cls, ctx):
    return capture_payment_intent(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="cancel", target="custom", arity="collection", bind=PaymentIntent)
def payment_intent__cancel(cls, ctx):
    return cancel_payment_intent(ctx, None, None, **(ctx.get("payload") or {}))


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([Invoice, InvoiceLineItem, PaymentIntent, Refund])
    return app


app = build_app(async_mode=True)
