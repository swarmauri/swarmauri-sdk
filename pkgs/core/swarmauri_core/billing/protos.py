"""Billing domain protocol models used for type annotations."""

from __future__ import annotations

from abc import ABC


class BillingProto(ABC):
    """Marker base class for billing protocol models."""

    __slots__ = ()


class ProductSpecProto(BillingProto):
    """Protocol model describing a product creation specification."""


class PriceSpecProto(BillingProto):
    """Protocol model describing a price configuration for a product."""


class CheckoutReqProto(BillingProto):
    """Protocol model describing a hosted checkout request payload."""


class ProductRefProto(BillingProto):
    """Protocol model representing a product identifier returned by a provider."""


class PriceRefProto(BillingProto):
    """Protocol model representing a price identifier returned by a provider."""


class CheckoutIntentProto(BillingProto):
    """Protocol model representing a hosted checkout intent."""


class PaymentIntentReqProto(BillingProto):
    """Protocol model describing an online payment intent request."""


class PaymentRefProto(BillingProto):
    """Protocol model representing a payment reference returned by a provider."""


class SubscriptionSpecProto(BillingProto):
    """Protocol model describing a subscription creation request."""


class InvoiceSpecProto(BillingProto):
    """Protocol model describing an invoice creation request."""


class SplitSpecProto(BillingProto):
    """Protocol model describing split configuration for marketplace charges."""


class RefundReqProto(BillingProto):
    """Protocol model describing a refund request."""


class CustomerSpecProto(BillingProto):
    """Protocol model describing a customer creation request."""


class CustomerRefProto(BillingProto):
    """Protocol model representing a customer identifier returned by a provider."""


class PaymentMethodSpecProto(BillingProto):
    """Protocol model describing a payment method creation request."""


class PaymentMethodRefProto(BillingProto):
    """Protocol model representing a payment method identifier returned by a provider."""


class PayoutReqProto(BillingProto):
    """Protocol model describing a payout request."""


class TransferReqProto(BillingProto):
    """Protocol model describing a balance transfer request."""


class BalanceRefProto(BillingProto):
    """Protocol model representing a balance snapshot returned by a provider."""


class ReportReqProto(BillingProto):
    """Protocol model describing a reports API request."""


class WebhookEventProto(BillingProto):
    """Protocol model representing a parsed webhook event."""


class CouponSpecProto(BillingProto):
    """Protocol model describing a coupon creation request."""


class PromotionSpecProto(BillingProto):
    """Protocol model describing a promotion creation request."""


__all__ = [
    "BillingProto",
    "ProductSpecProto",
    "PriceSpecProto",
    "CheckoutReqProto",
    "ProductRefProto",
    "PriceRefProto",
    "CheckoutIntentProto",
    "PaymentIntentReqProto",
    "PaymentRefProto",
    "SubscriptionSpecProto",
    "InvoiceSpecProto",
    "SplitSpecProto",
    "RefundReqProto",
    "CustomerSpecProto",
    "CustomerRefProto",
    "PaymentMethodSpecProto",
    "PaymentMethodRefProto",
    "PayoutReqProto",
    "TransferReqProto",
    "BalanceRefProto",
    "ReportReqProto",
    "WebhookEventProto",
    "CouponSpecProto",
    "PromotionSpecProto",
]
