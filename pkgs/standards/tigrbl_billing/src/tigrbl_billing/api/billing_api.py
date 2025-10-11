"""
Billing API composition using tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert are provided by tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle operations are bound via @op_ctx(bind=...).
"""

from tigrbl import TigrblApp, op_ctx
from tigrbl.engine.shortcuts import engine as build_engine, mem

# ---- Tables (models) ----
from tigrbl_billing.tables.product import Product
from tigrbl_billing.tables.price import Price
from tigrbl_billing.tables.price_tier import PriceTier
from tigrbl_billing.tables.feature import Feature
from tigrbl_billing.tables.price_feature_entitlement import PriceFeatureEntitlement
from tigrbl_billing.tables.customer import Customer
from tigrbl_billing.tables.subscription import Subscription
from tigrbl_billing.tables.subscription_item import SubscriptionItem
from tigrbl_billing.tables.seat_allocation import SeatAllocation
from tigrbl_billing.tables.usage_event import UsageEvent
from tigrbl_billing.tables.usage_rollup import UsageRollup
from tigrbl_billing.tables.invoice import Invoice
from tigrbl_billing.tables.invoice_line_item import InvoiceLineItem
from tigrbl_billing.tables.payment_intent import PaymentIntent
from tigrbl_billing.tables.refund import Refund
from tigrbl_billing.tables.checkout_session import CheckoutSession
from tigrbl_billing.tables.connected_account import ConnectedAccount
from tigrbl_billing.tables.customer_account_link import CustomerAccountLink
from tigrbl_billing.tables.split_rule import SplitRule
from tigrbl_billing.tables.transfer import Transfer
from tigrbl_billing.tables.webhook_endpoint import WebhookEndpoint
from tigrbl_billing.tables.application_fee import ApplicationFee
from tigrbl_billing.tables.stripe_event_log import StripeEventLog
from tigrbl_billing.tables.customer_balance import CustomerBalance
from tigrbl_billing.tables.balance_top_off import BalanceTopOff
from tigrbl_billing.tables.credit_grant import CreditGrant
from tigrbl_billing.tables.credit_usage_policy import CreditUsagePolicy
from tigrbl_billing.tables.credit_ledger import CreditLedger

# ---- Non-CRUD ops (from tigrbl_billing.ops) ----
from tigrbl_billing.ops import (
    create_or_link_customer,
    attach_payment_method,
    start_subscription,
    cancel_subscription,
    pause_subscription,
    resume_subscription,
    trial_start,
    trial_end,
    proration_preview,
    seat_assign,
    seat_release,
    seat_suspend,
    rollup_usage_periodic,
    finalize_invoice,
    void_invoice,
    mark_invoice_uncollectible,
    capture_payment_intent,
    cancel_payment_intent,
    refund_application_fee,
    ingest_webhook_event,
    sync_objects,
    request_top_off,
    apply_top_off,
    check_and_top_off,
    apply_grant,
    revoke_grant,
    charge_credits,
)


# -----------------------
# Customer account ops
# -----------------------
@op_ctx(alias="create_or_link", target="custom", arity="collection", bind=Customer)
def customer__create_or_link(cls, ctx):
    return create_or_link_customer(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(
    alias="attach_payment_method", target="custom", arity="collection", bind=Customer
)
def customer__attach_payment_method(cls, ctx):
    return attach_payment_method(ctx, None, None, **(ctx.get("payload") or {}))


# -----------------------
# Subscription lifecycle
# -----------------------
@op_ctx(alias="start", target="custom", arity="collection", bind=Subscription)
def subscription__start(cls, ctx):
    return start_subscription(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="cancel", target="custom", arity="collection", bind=Subscription)
def subscription__cancel(cls, ctx):
    return cancel_subscription(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="pause", target="custom", arity="collection", bind=Subscription)
def subscription__pause(cls, ctx):
    return pause_subscription(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="resume", target="custom", arity="collection", bind=Subscription)
def subscription__resume(cls, ctx):
    return resume_subscription(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="trial_start", target="custom", arity="collection", bind=Subscription)
def subscription__trial_start(cls, ctx):
    return trial_start(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="trial_end", target="custom", arity="collection", bind=Subscription)
def subscription__trial_end(cls, ctx):
    return trial_end(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(
    alias="proration_preview", target="custom", arity="collection", bind=Subscription
)
def subscription__proration_preview(cls, ctx):
    return proration_preview(ctx, None, None, **(ctx.get("payload") or {}))


# -----------------------
# Seats ledger
# -----------------------
@op_ctx(alias="assign", target="custom", arity="collection", bind=SeatAllocation)
def seat__assign(cls, ctx):
    return seat_assign(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="release", target="custom", arity="collection", bind=SeatAllocation)
def seat__release(cls, ctx):
    return seat_release(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="suspend", target="custom", arity="collection", bind=SeatAllocation)
def seat__suspend(cls, ctx):
    return seat_suspend(ctx, None, None, **(ctx.get("payload") or {}))


# -----------------------
# Usage (metered/usage-based)
# -----------------------
# NOTE: Usage events ingest uses default create on UsageEvent table.
@op_ctx(alias="rollup_periodic", target="custom", arity="collection", bind=UsageRollup)
def usage__rollup_periodic(cls, ctx):
    return rollup_usage_periodic(ctx, None, None, **(ctx.get("payload") or {}))


# -----------------------
# Invoice lifecycle (post-create)
# -----------------------
@op_ctx(alias="finalize", target="custom", arity="collection", bind=Invoice)
def invoice__finalize(cls, ctx):
    return finalize_invoice(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="void", target="custom", arity="collection", bind=Invoice)
def invoice__void(cls, ctx):
    return void_invoice(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="mark_uncollectible", target="custom", arity="collection", bind=Invoice)
def invoice__mark_uncollectible(cls, ctx):
    return mark_invoice_uncollectible(ctx, None, None, **(ctx.get("payload") or {}))


# -----------------------
# Payment intents lifecycle
# -----------------------
@op_ctx(alias="capture", target="custom", arity="collection", bind=PaymentIntent)
def payment_intent__capture(cls, ctx):
    return capture_payment_intent(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="cancel", target="custom", arity="collection", bind=PaymentIntent)
def payment_intent__cancel(cls, ctx):
    return cancel_payment_intent(ctx, None, None, **(ctx.get("payload") or {}))


# -----------------------
# Connect / application fee
# -----------------------
@op_ctx(
    alias="refund_app_fee", target="custom", arity="collection", bind=ApplicationFee
)
def application_fee__refund(cls, ctx):
    return refund_application_fee(ctx, None, None, **(ctx.get("payload") or {}))


# -----------------------
# Webhooks & object sync
# -----------------------
@op_ctx(alias="ingest", target="custom", arity="collection", bind=StripeEventLog)
def stripe_event_log__ingest(cls, ctx):
    return ingest_webhook_event(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="sync", target="custom", arity="collection", bind=Product)
def product__sync(cls, ctx):
    return sync_objects(ctx, None, None, **(ctx.get("payload") or {}))


# -----------------------
# App factory
# -----------------------
def build_billing_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models(
        [
            # Catalog
            Product,
            Price,
            PriceTier,
            Feature,
            PriceFeatureEntitlement,
            # Accounts & subscriptions
            Customer,
            Subscription,
            SubscriptionItem,
            # Seats & usage
            SeatAllocation,
            UsageEvent,
            UsageRollup,
            # Invoicing & payments
            Invoice,
            InvoiceLineItem,
            PaymentIntent,
            Refund,
            # Checkout
            CheckoutSession,
            # Connect
            ConnectedAccount,
            CustomerAccountLink,
            SplitRule,
            Transfer,
            # Webhooks & internal
            WebhookEndpoint,
            ApplicationFee,
            StripeEventLog,
        ]
    )
    return app


# Export ASGI app instance
app = build_billing_app(async_mode=True)


@op_ctx(
    alias="request_top_off", target="custom", arity="collection", bind=CustomerBalance
)
def _request_top_off(cls, ctx):
    return request_top_off(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="apply_top_off", target="custom", arity="collection", bind=BalanceTopOff)
def _apply_top_off(cls, ctx):
    return apply_top_off(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(
    alias="check_and_top_off", target="custom", arity="collection", bind=CustomerBalance
)
def _check_and_top_off(cls, ctx):
    return check_and_top_off(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="apply_grant", target="custom", arity="collection", bind=CreditGrant)
def _apply_grant(cls, ctx):
    return apply_grant(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="revoke_grant", target="custom", arity="collection", bind=CreditGrant)
def _revoke_grant(cls, ctx):
    return revoke_grant(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="charge_credits", target="custom", arity="collection", bind=UsageEvent)
def _charge_credits(cls, ctx):
    return charge_credits(ctx, None, None, **(ctx.get("payload") or {}))


def __extend_app(app):
    app.include_models(
        [CustomerBalance, BalanceTopOff, CreditGrant, CreditUsagePolicy, CreditLedger]
    )
    return app


app = __extend_app(app)
