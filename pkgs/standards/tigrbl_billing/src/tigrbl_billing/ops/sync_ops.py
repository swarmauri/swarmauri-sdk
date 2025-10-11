"""Sync ops – DB upserts from provided Stripe-like objects. External HTTP calls are intentionally excluded here."""
from __future__ import annotations
from typing import Iterable, Mapping, Sequence, Optional
from tigrbl.types import UUID
from tigrbl_billing.tables.product import Product
from tigrbl_billing.tables.price import Price, BillingScheme, RecurringInterval, UsageType, AggregateUsage, TaxBehavior
from tigrbl_billing.tables.price_tier import PriceTier
from tigrbl_billing.tables.customer import Customer
from tigrbl_billing.tables.subscription import Subscription, SubscriptionStatus, CollectionMethod
from tigrbl_billing.tables.subscription_item import SubscriptionItem
from tigrbl_billing.tables.invoice import Invoice, InvoiceStatus, CollectionMethod as InvoiceCollectionMethod
from tigrbl_billing.tables.invoice_line_item import InvoiceLineItem
from tigrbl_billing.tables.payment_intent import PaymentIntent, PaymentIntentStatus, CaptureMethod
from tigrbl_billing.tables.refund import Refund, RefundStatus
from tigrbl_billing.tables.connected_account import ConnectedAccount, AccountType
from tigrbl_billing.tables.transfer import Transfer
from tigrbl_billing.tables.application_fee import ApplicationFee
from contextlib import contextmanager
from typing import Any, Tuple
from tigrbl.types import Session

def _acquire(model, op_ctx) -> Tuple[Session, Any]:
    alias = getattr(op_ctx, 'alias', None) if op_ctx is not None else None
    db, release = model.acquire(op_alias=alias)
    return (db, release)

@contextmanager
def _session_for(model, op_ctx):
    db, release = _acquire(model, op_ctx)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        release()

def sync_objects(op_ctx, engine_ctx, schema_ctx, *, products: Optional[Sequence[Mapping]]=None, prices: Optional[Sequence[Mapping]]=None, price_tiers: Optional[Sequence[Mapping]]=None, customers: Optional[Sequence[Mapping]]=None, subscriptions: Optional[Sequence[Mapping]]=None, subscription_items: Optional[Sequence[Mapping]]=None, invoices: Optional[Sequence[Mapping]]=None, invoice_line_items: Optional[Sequence[Mapping]]=None, payment_intents: Optional[Sequence[Mapping]]=None, refunds: Optional[Sequence[Mapping]]=None, connected_accounts: Optional[Sequence[Mapping]]=None, transfers: Optional[Sequence[Mapping]]=None, application_fees: Optional[Sequence[Mapping]]=None) -> dict:
    """
    Bulk upsert provided objects into the local tables. Input maps should use the local schema field names.
    This op is **purely** DB-side to support repair/backfill jobs after webhook loss.
    """
    results = {}
    if products:
        with _session_for(Product, op_ctx) as db:
            for r in products:
                obj = None
                sid = r.get('stripe_product_id')
                if sid and hasattr(db, 'query'):
                    obj = db.query(Product).filter(Product.stripe_product_id == sid).one_or_none()
                if obj is None:
                    obj = Product(**r)
                else:
                    for k, v in r.items():
                        setattr(obj, k, v)
                db.add(obj)
                db.flush()
            results['products'] = len(products)
    if prices:
        with _session_for(Price, op_ctx) as db:
            for r in prices:
                sid = r.get('stripe_price_id')
                obj = None
                if sid and hasattr(db, 'query'):
                    obj = db.query(Price).filter(Price.stripe_price_id == sid).one_or_none()
                if obj is None:
                    obj = Price(**r)
                else:
                    for k, v in r.items():
                        setattr(obj, k, v)
                db.add(obj)
                db.flush()
            results['prices'] = len(prices)
    if price_tiers:
        with _session_for(PriceTier, op_ctx) as db:
            for r in price_tiers:
                db.add(PriceTier(**r))
                db.flush()
            results['price_tiers'] = len(price_tiers)
    if customers:
        with _session_for(Customer, op_ctx) as db:
            for r in customers:
                sid = r.get('stripe_customer_id')
                obj = None
                if sid and hasattr(db, 'query'):
                    obj = db.query(Customer).filter(Customer.stripe_customer_id == sid).one_or_none()
                if obj is None:
                    obj = Customer(**r)
                else:
                    for k, v in r.items():
                        setattr(obj, k, v)
                db.add(obj)
                db.flush()
            results['customers'] = len(customers)
    if subscriptions:
        with _session_for(Subscription, op_ctx) as db:
            for r in subscriptions:
                sid = r.get('stripe_subscription_id')
                obj = None
                if sid and hasattr(db, 'query'):
                    obj = db.query(Subscription).filter(Subscription.stripe_subscription_id == sid).one_or_none()
                if obj is None:
                    obj = Subscription(**r)
                else:
                    for k, v in r.items():
                        setattr(obj, k, v)
                db.add(obj)
                db.flush()
            results['subscriptions'] = len(subscriptions)
    if subscription_items:
        with _session_for(SubscriptionItem, op_ctx) as db:
            for r in subscription_items:
                sid = r.get('stripe_subscription_item_id')
                obj = None
                if sid and hasattr(db, 'query'):
                    obj = db.query(SubscriptionItem).filter(SubscriptionItem.stripe_subscription_item_id == sid).one_or_none()
                if obj is None:
                    obj = SubscriptionItem(**r)
                else:
                    for k, v in r.items():
                        setattr(obj, k, v)
                db.add(obj)
                db.flush()
            results['subscription_items'] = len(subscription_items)
    if invoices:
        with _session_for(Invoice, op_ctx) as db:
            for r in invoices:
                sid = r.get('stripe_invoice_id')
                obj = None
                if sid and hasattr(db, 'query'):
                    obj = db.query(Invoice).filter(Invoice.stripe_invoice_id == sid).one_or_none()
                if obj is None:
                    obj = Invoice(**r)
                else:
                    for k, v in r.items():
                        setattr(obj, k, v)
                db.add(obj)
                db.flush()
            results['invoices'] = len(invoices)
    if invoice_line_items:
        with _session_for(InvoiceLineItem, op_ctx) as db:
            for r in invoice_line_items:
                db.add(InvoiceLineItem(**r))
                db.flush()
            results['invoice_line_items'] = len(invoice_line_items)
    if payment_intents:
        with _session_for(PaymentIntent, op_ctx) as db:
            for r in payment_intents:
                sid = r.get('stripe_payment_intent_id')
                obj = None
                if sid and hasattr(db, 'query'):
                    obj = db.query(PaymentIntent).filter(PaymentIntent.stripe_payment_intent_id == sid).one_or_none()
                if obj is None:
                    obj = PaymentIntent(**r)
                else:
                    for k, v in r.items():
                        setattr(obj, k, v)
                db.add(obj)
                db.flush()
            results['payment_intents'] = len(payment_intents)
    if refunds:
        with _session_for(Refund, op_ctx) as db:
            for r in refunds:
                sid = r.get('stripe_refund_id')
                obj = None
                if sid and hasattr(db, 'query'):
                    obj = db.query(Refund).filter(Refund.stripe_refund_id == sid).one_or_none()
                if obj is None:
                    obj = Refund(**r)
                else:
                    for k, v in r.items():
                        setattr(obj, k, v)
                db.add(obj)
                db.flush()
            results['refunds'] = len(refunds)
    if connected_accounts:
        with _session_for(ConnectedAccount, op_ctx) as db:
            for r in connected_accounts:
                sid = r.get('stripe_account_id')
                obj = None
                if sid and hasattr(db, 'query'):
                    obj = db.query(ConnectedAccount).filter(ConnectedAccount.stripe_account_id == sid).one_or_none()
                if obj is None:
                    obj = ConnectedAccount(**r)
                else:
                    for k, v in r.items():
                        setattr(obj, k, v)
                db.add(obj)
                db.flush()
            results['connected_accounts'] = len(connected_accounts)
    if transfers:
        with _session_for(Transfer, op_ctx) as db:
            for r in transfers:
                sid = r.get('stripe_transfer_id')
                obj = None
                if sid and hasattr(db, 'query'):
                    obj = db.query(Transfer).filter(Transfer.stripe_transfer_id == sid).one_or_none()
                if obj is None:
                    obj = Transfer(**r)
                else:
                    for k, v in r.items():
                        setattr(obj, k, v)
                db.add(obj)
                db.flush()
            results['transfers'] = len(transfers)
    if application_fees:
        with _session_for(ApplicationFee, op_ctx) as db:
            for r in application_fees:
                sid = r.get('stripe_application_fee_id')
                obj = None
                if sid and hasattr(db, 'query'):
                    obj = db.query(ApplicationFee).filter(ApplicationFee.stripe_application_fee_id == sid).one_or_none()
                if obj is None:
                    obj = ApplicationFee(**r)
                else:
                    for k, v in r.items():
                        setattr(obj, k, v)
                db.add(obj)
                db.flush()
            results['application_fees'] = len(application_fees)
    return results