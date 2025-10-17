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
    name: Optional[str] = Field(
        default=None, description="Human-friendly product name returned by the provider"
    )
    description: Optional[str] = Field(
        default=None, description="Product description supplied by the provider"
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Provider metadata associated with the product"
    )


class PriceRef(PriceRefProto, BillingRef):
    """Reference to a price record managed by a billing provider."""

    id: str = Field(..., description="Provider-specific price identifier")
    product_id: Optional[str] = Field(
        default=None, description="Identifier of the product this price belongs to"
    )
    currency: Optional[str] = Field(
        default=None, description="Currency code for the price"
    )
    unit_amount_minor: Optional[int] = Field(
        default=None, description="Unit amount in the smallest currency denomination"
    )


class CheckoutIntentRef(CheckoutIntentProto, BillingRef):
    """Reference to a hosted checkout intent."""

    id: str = Field(..., description="Provider-specific checkout intent identifier")
    url: Optional[str] = Field(
        default=None, description="URL where the customer should complete the checkout"
    )


class PaymentRef(PaymentRefProto, BillingRef):
    """Reference to a payment intent or object."""

    id: str = Field(..., description="Provider-specific payment identifier")
    status: Optional[str] = Field(
        default=None, description="Provider-specific payment status"
    )
    amount_minor: Optional[int] = Field(
        default=None,
        description="Amount associated with the payment in the smallest currency denomination",
    )
    currency: Optional[str] = Field(
        default=None, description="Currency code for the payment"
    )


class CustomerRef(CustomerRefProto, BillingRef):
    """Reference to a customer profile."""

    id: str = Field(..., description="Provider-specific customer identifier")
    email: Optional[str] = Field(default=None, description="Customer email address")
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Provider metadata associated with the customer"
    )


class PaymentMethodRef(PaymentMethodRefProto, BillingRef):
    """Reference to a payment method record."""

    id: str = Field(..., description="Provider-specific payment method identifier")
    type: Optional[str] = Field(
        default=None, description="Payment method type returned by the provider"
    )


class BalanceRef(BalanceRefProto, BillingRef):
    """Reference describing a balance snapshot."""

    snapshot_id: str = Field(..., description="Identifier for the balance snapshot")
    currency: Optional[str] = Field(
        default=None, description="Currency code for the balance amounts"
    )
    available_minor: Optional[int] = Field(
        default=None,
        description="Available balance in the smallest currency denomination",
    )


class WebhookEventRef(WebhookEventProto, BillingRef):
    """Reference representing a parsed webhook event."""

    event_id: str = Field(..., description="Event identifier returned by the provider")
    type: Optional[str] = Field(default=None, description="Provider event type")
