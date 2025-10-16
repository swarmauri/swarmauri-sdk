"""Pydantic reference models returned by billing mixins."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from pydantic import BaseModel, ConfigDict, Field

from swarmauri_core.billing.protos import (
    BalanceRefProto,
    CheckoutIntentProto,
    CustomerRefProto,
    PaymentMethodRefProto,
    PaymentRefProto,
    PriceRefProto,
    ProductRefProto,
    WebhookEventProto,
)


class BillingRef(BaseModel):
    """Base class shared across billing reference models."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    provider: str = Field(..., description="Identifier for the billing provider")
    raw: Mapping[str, Any] = Field(
        default_factory=dict,
        description="Raw provider payload used to derive this reference.",
    )


class ProductRef(ProductRefProto, BillingRef):
    """Reference to a product managed by a billing provider."""

    id: str = Field(..., description="Provider-specific product identifier")


class PriceRef(PriceRefProto, BillingRef):
    """Reference to a price record managed by a billing provider."""

    id: str = Field(..., description="Provider-specific price identifier")


class CheckoutIntentRef(CheckoutIntentProto, BillingRef):
    """Reference to a hosted checkout intent."""

    id: str = Field(..., description="Provider-specific checkout intent identifier")


class PaymentRef(PaymentRefProto, BillingRef):
    """Reference to a payment intent or object."""

    id: str = Field(..., description="Provider-specific payment identifier")


class CustomerRef(CustomerRefProto, BillingRef):
    """Reference to a customer profile."""

    id: str = Field(..., description="Provider-specific customer identifier")


class PaymentMethodRef(PaymentMethodRefProto, BillingRef):
    """Reference to a payment method record."""

    id: str = Field(..., description="Provider-specific payment method identifier")


class BalanceRef(BalanceRefProto, BillingRef):
    """Reference describing a balance snapshot."""

    snapshot_id: str = Field(..., description="Identifier for the balance snapshot")


class WebhookEventRef(WebhookEventProto, BillingRef):
    """Reference representing a parsed webhook event."""

    event_id: str = Field(..., description="Event identifier returned by the provider")
    type: Optional[str] = Field(default=None, description="Provider event type")
