"""
API for a specific billing strategy, built with tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert use tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle ops load decorated helpers from ``tigrbl_billing.ops`` on demand.
"""

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing.tables.invoice import Invoice
from tigrbl_billing.tables.invoice_line_item import InvoiceLineItem
from tigrbl_billing.tables.payment_intent import PaymentIntent
from tigrbl_billing.tables.refund import Refund

from tigrbl_billing import ops

# Register only the invoice and payment intent operations this API needs.
ops.finalize_invoice
ops.void_invoice
ops.mark_invoice_uncollectible
ops.capture_payment_intent
ops.cancel_payment_intent


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([Invoice, InvoiceLineItem, PaymentIntent, Refund])
    return app


app = build_app(async_mode=True)
