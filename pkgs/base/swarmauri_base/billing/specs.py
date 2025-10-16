"""Generic specification models used by billing mixins."""

from __future__ import annotations

from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field

from swarmauri_core.billing.protos import (
    CheckoutReqProto,
    CouponSpecProto,
    CustomerSpecProto,
    InvoiceSpecProto,
    PaymentIntentReqProto,
    PaymentMethodSpecProto,
    PayoutReqProto,
    PriceSpecProto,
    ProductSpecProto,
    PromotionSpecProto,
    RefundReqProto,
    ReportReqProto,
    SplitSpecProto,
    SubscriptionSpecProto,
    TransferReqProto,
)


class BillingSpec(BaseModel):
    """Base class for provider-agnostic billing specifications."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    payload: Mapping[str, Any] = Field(
        default_factory=dict,
        description="Provider-agnostic payload forwarded to the billing API.",
    )


class ProductSpec(ProductSpecProto, BillingSpec):
    """Product creation specification."""


class PriceSpec(PriceSpecProto, BillingSpec):
    """Price creation specification."""


class CheckoutRequest(CheckoutReqProto, BillingSpec):
    """Hosted checkout request specification."""


class PaymentIntentRequest(PaymentIntentReqProto, BillingSpec):
    """Payment intent request specification."""


class SubscriptionSpec(SubscriptionSpecProto, BillingSpec):
    """Subscription creation specification."""


class InvoiceSpec(InvoiceSpecProto, BillingSpec):
    """Invoice creation specification."""


class SplitSpec(SplitSpecProto, BillingSpec):
    """Split configuration specification for marketplace operations."""


class RefundRequest(RefundReqProto, BillingSpec):
    """Refund request specification."""


class CustomerSpec(CustomerSpecProto, BillingSpec):
    """Customer creation specification."""


class PaymentMethodSpec(PaymentMethodSpecProto, BillingSpec):
    """Payment method creation specification."""


class PayoutRequest(PayoutReqProto, BillingSpec):
    """Payout request specification."""


class TransferRequest(TransferReqProto, BillingSpec):
    """Balance transfer request specification."""


class ReportRequest(ReportReqProto, BillingSpec):
    """Report creation request specification."""


class CouponSpec(CouponSpecProto, BillingSpec):
    """Coupon creation specification."""


class PromotionSpec(PromotionSpecProto, BillingSpec):
    """Promotion creation specification."""
