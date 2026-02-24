"""Enumerations and capability mapping shared across billing providers."""

from __future__ import annotations

from enum import Enum
from typing import Dict, FrozenSet, Iterable


class Capability(str, Enum):
    """Provider capability identifiers exposed by Swarmauri billing providers."""

    PRODUCTS_PRICES = "products_prices"
    HOSTED_CHECKOUT = "hosted_checkout"
    ONLINE_PAYMENTS = "online_payments"
    SUBSCRIPTIONS = "subscriptions"
    INVOICING = "invoicing"
    MARKETPLACE = "marketplace"
    RISK = "risk"
    REFUNDS = "refunds"
    CUSTOMERS = "customers"
    PAYMENT_METHODS = "payment_methods"
    PAYOUTS = "payouts"
    BALANCE_TRANSFERS = "balance_transfers"
    REPORTS = "reports"
    WEBHOOKS = "webhooks"
    PROMOTIONS = "promotions"


class Operation(str, Enum):
    """Dispatch operations handled by a billing provider implementation."""

    CREATE_PRODUCT = "create_product"
    CREATE_PRICE = "create_price"
    CREATE_CHECKOUT = "create_checkout"
    CREATE_PAYMENT_INTENT = "create_payment_intent"
    CAPTURE_PAYMENT = "capture_payment"
    CANCEL_PAYMENT = "cancel_payment"
    CREATE_SUBSCRIPTION = "create_subscription"
    CANCEL_SUBSCRIPTION = "cancel_subscription"
    CREATE_INVOICE = "create_invoice"
    FINALIZE_INVOICE = "finalize_invoice"
    VOID_INVOICE = "void_invoice"
    MARK_UNCOLLECTIBLE = "mark_uncollectible"
    CREATE_SPLIT = "create_split"
    CHARGE_WITH_SPLIT = "charge_with_split"
    VERIFY_WEBHOOK_SIGNATURE = "verify_webhook_signature"
    LIST_DISPUTES = "list_disputes"
    CREATE_REFUND = "create_refund"
    GET_REFUND = "get_refund"
    CREATE_CUSTOMER = "create_customer"
    GET_CUSTOMER = "get_customer"
    ATTACH_PM_TO_CUSTOMER = "attach_payment_method_to_customer"
    CREATE_PAYMENT_METHOD = "create_payment_method"
    DETACH_PAYMENT_METHOD = "detach_payment_method"
    LIST_PAYMENT_METHODS = "list_payment_methods"
    CREATE_PAYOUT = "create_payout"
    GET_BALANCE = "get_balance"
    CREATE_TRANSFER = "create_transfer"
    CREATE_REPORT = "create_report"
    PARSE_EVENT = "parse_event"
    CREATE_COUPON = "create_coupon"
    CREATE_PROMOTION = "create_promotion"


ALL_CAPABILITIES: FrozenSet[Capability] = frozenset(cap for cap in Capability)
"""Complete set of billing capabilities."""


# Mapping from Swarmauri billing capabilities to tigrbl_billing capability identifiers.
# Keeping the mapping in string form avoids importing the tigrbl package as a runtime dependency.
CAPABILITY_TO_TIGRBL: Dict[Capability, FrozenSet[str]] = {
    Capability.PRODUCTS_PRICES: frozenset({"PRICE"}),
    Capability.HOSTED_CHECKOUT: frozenset({"CHARGE"}),
    Capability.ONLINE_PAYMENTS: frozenset({"CHARGE", "REFUND", "PARTIAL_REFUND"}),
    Capability.SUBSCRIPTIONS: frozenset({"SUBS_BASIC", "SUBS_TRIALS"}),
    Capability.INVOICING: frozenset({"INVOICE_PAYMENT"}),
    Capability.MARKETPLACE: frozenset({"PAYMENT_SPLIT", "TRANSFER"}),
    Capability.RISK: frozenset(),
    Capability.REFUNDS: frozenset({"REFUND", "PARTIAL_REFUND"}),
    Capability.CUSTOMERS: frozenset({"CONNECTED_ACCOUNTS"}),
    Capability.PAYMENT_METHODS: frozenset({"PRICE"}),
    Capability.PAYOUTS: frozenset({"TRANSFER"}),
    Capability.BALANCE_TRANSFERS: frozenset({"TRANSFER"}),
    Capability.REPORTS: frozenset(),
    Capability.WEBHOOKS: frozenset(),
    Capability.PROMOTIONS: frozenset(),
}
"""Map capability identifiers to the underlying tigrbl API capability names."""


def capabilities_to_tigrbl(capabilities: Iterable[Capability]) -> FrozenSet[str]:
    """Translate Swarmauri billing capabilities to tigrbl capability identifiers."""

    mapped = set()
    for capability in capabilities:
        mapped.update(CAPABILITY_TO_TIGRBL.get(capability, frozenset()))
    return frozenset(mapped)
