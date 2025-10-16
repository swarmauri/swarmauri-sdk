"""Pydantic models used by billing provider mixins."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from pydantic import BaseModel, ConfigDict, Field

from swarmauri_core.billing.interfaces import (
    CheckoutIntentProto,
    CheckoutReqProto,
    CustomerRefProto,
    CustomerSpecProto,
    CouponSpecProto,
    InvoiceSpecProto,
    BalanceRefProto,
    PaymentIntentReqProto,
    PaymentMethodRefProto,
    PaymentMethodSpecProto,
    PaymentRefProto,
    PayoutReqProto,
    PriceRefProto,
    PriceSpecProto,
    ProductRefProto,
    ProductSpecProto,
    PromotionSpecProto,
    RefundReqProto,
    ReportReqProto,
    SplitSpecProto,
    SubscriptionSpecProto,
    TransferReqProto,
    WebhookEventProto,
)


class BillingModel(BaseModel):
    """Common base model enabling pydantic serialisation for billing types."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True, extra="ignore", populate_by_name=True
    )


class ProductSpec(BillingModel, ProductSpecProto):
    """Local product specification shape."""

    name: str
    description: Optional[str] = None
    sku: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class PriceSpec(BillingModel, PriceSpecProto):
    """Local price specification shape."""

    currency: str
    unit_amount_minor: int
    nickname: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class CheckoutRequest(BillingModel, CheckoutReqProto):
    """Hosted checkout request."""

    quantity: int = 1
    success_url: str
    cancel_url: str
    customer_email: Optional[str] = None
    idempotency_key: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class ProductRef(BillingModel, ProductRefProto):
    """Reference returned by providers when a product is created."""

    id: str
    provider: Optional[str] = None
    raw: Optional[Any] = None


class PriceRef(BillingModel, PriceRefProto):
    """Reference returned by providers when a price is created."""

    id: str
    product_id: Optional[str] = None
    provider: Optional[str] = None
    raw: Optional[Any] = None


class CheckoutIntent(BillingModel, CheckoutIntentProto):
    """Reference returned for a hosted checkout session."""

    id: Optional[str] = None
    url: Optional[str] = None
    client_secret: Optional[str] = None
    provider: Optional[str] = None
    raw: Optional[Any] = None


class PaymentIntentRequest(BillingModel, PaymentIntentReqProto):
    """Payment intent request parameters."""

    amount_minor: int
    currency: str
    confirm: bool = False
    capture: bool = True
    payment_method_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class PaymentRef(BillingModel, PaymentRefProto):
    """Reference returned when working with payments."""

    id: str
    status: Optional[str] = None
    provider: Optional[str] = None
    raw: Optional[Any] = None


class SubscriptionItem(BillingModel):
    """Line item for a subscription."""

    price_id: str
    quantity: int = 1


class SubscriptionSpec(BillingModel, SubscriptionSpecProto):
    """Subscription creation specification."""

    customer_id: str
    items: List[SubscriptionItem]
    trial_end: Optional[int] = None
    collection_method: str = "charge_automatically"
    metadata: Dict[str, str] = Field(default_factory=dict)
    idempotency_key: Optional[str] = None


class InvoiceLineItem(BillingModel):
    """Invoice line item specification."""

    price_id: Optional[str] = None
    amount_minor: Optional[int] = None
    quantity: int = 1
    description: Optional[str] = None


class InvoiceSpec(BillingModel, InvoiceSpecProto):
    """Invoice creation specification."""

    customer_id: str
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    collection_method: str = "send_invoice"
    days_until_due: Optional[int] = 14
    metadata: Dict[str, str] = Field(default_factory=dict)
    idempotency_key: Optional[str] = None


class SplitEntry(BillingModel):
    """Entry describing how a split payment is distributed."""

    account: str
    share: float


class SplitSpec(BillingModel, SplitSpecProto):
    """Marketplace split configuration."""

    name: str
    currency: str
    entries: List[SplitEntry]
    type: str = "percentage"
    idempotency_key: Optional[str] = None


class RefundRequest(BillingModel, RefundReqProto):
    """Refund request payload."""

    amount_minor: Optional[int] = None
    reason: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class CustomerSpec(BillingModel, CustomerSpecProto):
    """Customer creation specification."""

    email: Optional[str] = None
    name: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class CustomerRef(BillingModel, CustomerRefProto):
    """Customer reference returned by providers."""

    id: str
    provider: Optional[str] = None
    raw: Optional[Any] = None


class PaymentMethodSpec(BillingModel, PaymentMethodSpecProto):
    """Payment method creation specification."""

    type: str
    details: Mapping[str, Any]


class PaymentMethodRef(BillingModel, PaymentMethodRefProto):
    """Payment method reference returned by providers."""

    id: str
    provider: Optional[str] = None
    raw: Optional[Any] = None


class PayoutRequest(BillingModel, PayoutReqProto):
    """Payout request specification."""

    amount_minor: int
    currency: str
    destination: str
    metadata: Dict[str, str] = Field(default_factory=dict)


class TransferRequest(BillingModel, TransferReqProto):
    """Transfer request specification."""

    amount_minor: int
    currency: str
    destination: str
    metadata: Dict[str, str] = Field(default_factory=dict)


class BalanceRef(BillingModel, BalanceRefProto):
    """Balance snapshot returned by providers."""

    snapshot_id: str
    provider: Optional[str] = None
    raw: Optional[Any] = None


class ReportRequest(BillingModel, ReportReqProto):
    """Report request specification."""

    report_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class WebhookEvent(BillingModel, WebhookEventProto):
    """Webhook event wrapper."""

    event_id: str
    provider: Optional[str] = None
    raw: Optional[Any] = None


class CouponSpec(BillingModel, CouponSpecProto):
    """Coupon creation specification."""

    code: str
    metadata: Dict[str, str] = Field(default_factory=dict)


class PromotionSpec(BillingModel, PromotionSpecProto):
    """Promotion creation specification."""

    name: str
    metadata: Dict[str, str] = Field(default_factory=dict)


__all__ = [
    "BalanceRef",
    "CheckoutIntent",
    "CheckoutRequest",
    "CouponSpec",
    "CustomerRef",
    "CustomerSpec",
    "InvoiceLineItem",
    "InvoiceSpec",
    "PaymentIntentRequest",
    "PaymentMethodRef",
    "PaymentMethodSpec",
    "PaymentRef",
    "PayoutRequest",
    "PriceRef",
    "PriceSpec",
    "ProductRef",
    "ProductSpec",
    "PromotionSpec",
    "RefundRequest",
    "ReportRequest",
    "SplitEntry",
    "SplitSpec",
    "SubscriptionItem",
    "SubscriptionSpec",
    "TransferRequest",
    "WebhookEvent",
]
