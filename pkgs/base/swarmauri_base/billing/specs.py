"""Generic specification models used by billing mixins."""

from __future__ import annotations

from typing import Any, List, Mapping, Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

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

    def _apply_payload_defaults(self, field_names: Sequence[str]) -> None:
        """Populate unset attributes from ``payload`` when possible."""

        data = self.payload if isinstance(self.payload, Mapping) else {}
        for field in field_names:
            if getattr(self, field, None) is None and field in data:
                object.__setattr__(self, field, data[field])

    def resolve(self, field: str, default: Any = None) -> Any:
        """Return ``field`` either from the attribute or from ``payload``."""

        value = getattr(self, field, None)
        if value is not None:
            return value
        if isinstance(self.payload, Mapping):
            return self.payload.get(field, default)
        return default


class ProductSpec(ProductSpecProto, BillingSpec):
    """Product creation specification."""

    name: Optional[str] = Field(default=None, description="Product display name")
    description: Optional[str] = Field(
        default=None, description="Detailed description of the product"
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Metadata to associate with the product"
    )
    sku: Optional[str] = Field(
        default=None, description="Optional SKU identifier for inventory systems"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "ProductSpec":
        self._apply_payload_defaults(["name", "description", "metadata", "sku"])
        return self


class PriceSpec(PriceSpecProto, BillingSpec):
    """Price creation specification."""

    currency: Optional[str] = Field(
        default=None, description="ISO currency code for the price"
    )
    unit_amount_minor: Optional[int] = Field(
        default=None,
        description="Unit amount represented in the currency's smallest denomination",
    )
    nickname: Optional[str] = Field(
        default=None, description="Optional nickname for the price"
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Metadata to associate with the price"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "PriceSpec":
        self._apply_payload_defaults(
            ["currency", "unit_amount_minor", "nickname", "metadata"]
        )
        return self


class CheckoutRequest(CheckoutReqProto, BillingSpec):
    """Hosted checkout request specification."""

    quantity: int = Field(default=1, description="Quantity of the price to purchase")
    success_url: Optional[str] = Field(
        default=None, description="URL the customer is redirected to after success"
    )
    cancel_url: Optional[str] = Field(
        default=None, description="URL the customer is redirected to after cancellation"
    )
    customer_email: Optional[str] = Field(
        default=None, description="Customer email used for the checkout session"
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Metadata forwarded to the provider checkout"
    )
    idempotency_key: Optional[str] = Field(
        default=None, description="Optional idempotency key for the checkout session"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "CheckoutRequest":
        self._apply_payload_defaults(
            [
                "quantity",
                "success_url",
                "cancel_url",
                "customer_email",
                "metadata",
                "idempotency_key",
            ]
        )
        return self


class PaymentIntentRequest(PaymentIntentReqProto, BillingSpec):
    """Payment intent request specification."""

    amount_minor: Optional[int] = Field(
        default=None,
        description="Amount to collect in the currency's smallest denomination",
    )
    currency: Optional[str] = Field(
        default=None, description="ISO currency code for the payment"
    )
    payment_method_id: Optional[str] = Field(
        default=None, description="Identifier of an existing payment method"
    )
    confirm: bool = Field(default=False, description="Whether to confirm immediately")
    capture: bool = Field(
        default=True,
        description="Whether to auto-capture the payment upon confirmation",
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Provider-specific metadata to attach to the payment"
    )
    idempotency_key: Optional[str] = Field(
        default=None, description="Optional idempotency key for the payment intent"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "PaymentIntentRequest":
        self._apply_payload_defaults(
            [
                "amount_minor",
                "currency",
                "payment_method_id",
                "confirm",
                "capture",
                "metadata",
                "idempotency_key",
            ]
        )
        return self


class SubscriptionItemSpec(BaseModel):
    """Individual subscription item entry."""

    price_id: str = Field(..., description="Identifier of the price to subscribe to")
    quantity: int = Field(default=1, description="Quantity for the subscription item")


class SubscriptionSpec(SubscriptionSpecProto, BillingSpec):
    """Subscription creation specification."""

    customer_id: Optional[str] = Field(
        default=None, description="Identifier for the subscribing customer"
    )
    items: Sequence[SubscriptionItemSpec] = Field(
        default_factory=tuple,
        description="Collection of subscription items to provision",
    )
    trial_end: Optional[int] = Field(
        default=None,
        description="Unix timestamp indicating when a trial should end",
    )
    collection_method: Optional[str] = Field(
        default=None,
        description="Collection method accepted by the provider (e.g. charge_automatically)",
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Metadata associated with the subscription"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "SubscriptionSpec":
        self._apply_payload_defaults(
            ["customer_id", "trial_end", "collection_method", "metadata"]
        )
        if (
            not self.items
            and isinstance(self.payload, Mapping)
            and "items" in self.payload
        ):
            entries = [
                item
                if isinstance(item, SubscriptionItemSpec)
                else SubscriptionItemSpec(**item)
                for item in self.payload.get("items", [])
            ]
            object.__setattr__(self, "items", tuple(entries))
        return self


class InvoiceLineItemSpec(BaseModel):
    """Invoice line item specification."""

    price_id: Optional[str] = Field(
        default=None, description="Identifier of an existing price to reference"
    )
    amount_minor: Optional[int] = Field(
        default=None,
        description="Explicit amount in the smallest currency denomination",
    )
    currency: Optional[str] = Field(
        default=None, description="Currency for custom invoice line items"
    )
    description: Optional[str] = Field(
        default=None, description="Description shown on the invoice line"
    )
    quantity: int = Field(default=1, description="Quantity for the line item")


class InvoiceSpec(InvoiceSpecProto, BillingSpec):
    """Invoice creation specification."""

    customer_id: Optional[str] = Field(
        default=None, description="Identifier for the customer receiving the invoice"
    )
    collection_method: Optional[str] = Field(
        default=None, description="Invoice collection method"
    )
    days_until_due: Optional[int] = Field(
        default=None, description="Number of days until the invoice is due"
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Metadata attached to the invoice"
    )
    line_items: Sequence[InvoiceLineItemSpec] = Field(
        default_factory=tuple,
        description="Line items that make up the invoice",
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "InvoiceSpec":
        self._apply_payload_defaults(
            ["customer_id", "collection_method", "days_until_due", "metadata"]
        )
        if not self.line_items and isinstance(self.payload, Mapping):
            payload_items = self.payload.get("line_items", [])
            items: List[InvoiceLineItemSpec] = []
            for item in payload_items:
                if isinstance(item, InvoiceLineItemSpec):
                    items.append(item)
                else:
                    items.append(InvoiceLineItemSpec(**item))
            object.__setattr__(self, "line_items", tuple(items))
        return self


class SplitEntrySpec(BaseModel):
    """Individual split entry for marketplace operations."""

    account: str = Field(..., description="Destination account for the split")
    share: float = Field(
        ..., description="Relative share or percentage to allocate to the account"
    )


class SplitSpec(SplitSpecProto, BillingSpec):
    """Split configuration specification for marketplace operations."""

    name: Optional[str] = Field(default=None, description="Human readable split name")
    type: Optional[str] = Field(
        default=None, description="Provider-specific split type"
    )
    currency: Optional[str] = Field(
        default=None, description="Currency that the split applies to"
    )
    entries: Sequence[SplitEntrySpec] = Field(
        default_factory=tuple,
        description="Entries that participate in the split",
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "SplitSpec":
        self._apply_payload_defaults(["name", "type", "currency"])
        if not self.entries and isinstance(self.payload, Mapping):
            payload_entries = self.payload.get("entries", [])
            entries = [
                entry if isinstance(entry, SplitEntrySpec) else SplitEntrySpec(**entry)
                for entry in payload_entries
            ]
            object.__setattr__(self, "entries", tuple(entries))
        return self


class RefundRequest(RefundReqProto, BillingSpec):
    """Refund request specification."""

    amount_minor: Optional[int] = Field(
        default=None,
        description="Amount to refund in the smallest currency denomination",
    )
    reason: Optional[str] = Field(
        default=None, description="Reason for issuing the refund"
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Metadata associated with the refund"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "RefundRequest":
        self._apply_payload_defaults(["amount_minor", "reason", "metadata"])
        return self


class CustomerSpec(CustomerSpecProto, BillingSpec):
    """Customer creation specification."""

    name: Optional[str] = Field(default=None, description="Customer full name")
    email: Optional[str] = Field(default=None, description="Customer email address")
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Metadata associated with the customer"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "CustomerSpec":
        self._apply_payload_defaults(["name", "email", "metadata"])
        return self


class PaymentMethodSpec(PaymentMethodSpecProto, BillingSpec):
    """Payment method creation specification."""

    type: Optional[str] = Field(default=None, description="Payment method type")
    billing_details: Mapping[str, Any] | None = Field(
        default=None, description="Billing details associated with the payment method"
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Metadata attached to the payment method"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "PaymentMethodSpec":
        self._apply_payload_defaults(["type", "billing_details", "metadata"])
        return self


class PayoutRequest(PayoutReqProto, BillingSpec):
    """Payout request specification."""

    amount_minor: Optional[int] = Field(
        default=None,
        description="Amount to pay out in the smallest currency denomination",
    )
    currency: Optional[str] = Field(default=None, description="Currency of the payout")
    destination_account: Optional[str] = Field(
        default=None, description="Destination account identifier for the payout"
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Metadata attached to the payout"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "PayoutRequest":
        self._apply_payload_defaults(
            ["amount_minor", "currency", "destination_account", "metadata"]
        )
        return self


class TransferRequest(TransferReqProto, BillingSpec):
    """Balance transfer request specification."""

    amount_minor: Optional[int] = Field(
        default=None,
        description="Amount to transfer in the currency's smallest denomination",
    )
    currency: Optional[str] = Field(
        default=None, description="Currency of the transfer"
    )
    destination_account: Optional[str] = Field(
        default=None, description="Destination account receiving the transfer"
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Metadata associated with the transfer"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "TransferRequest":
        self._apply_payload_defaults(
            ["amount_minor", "currency", "destination_account", "metadata"]
        )
        return self


class ReportRequest(ReportReqProto, BillingSpec):
    """Report creation request specification."""

    report_type: Optional[str] = Field(
        default=None, description="Provider-specific report type identifier"
    )
    parameters: Mapping[str, Any] | None = Field(
        default=None, description="Additional provider parameters"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "ReportRequest":
        self._apply_payload_defaults(["report_type", "parameters"])
        return self


class CouponSpec(CouponSpecProto, BillingSpec):
    """Coupon creation specification."""

    percent_off: Optional[float] = Field(
        default=None, description="Percentage discount for the coupon"
    )
    amount_off_minor: Optional[int] = Field(
        default=None,
        description="Fixed amount discount in the smallest currency denomination",
    )
    currency: Optional[str] = Field(
        default=None, description="Currency for fixed-amount coupons"
    )
    duration: Optional[str] = Field(
        default=None, description="Duration for which the coupon applies"
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Metadata attached to the coupon"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "CouponSpec":
        self._apply_payload_defaults(
            ["percent_off", "amount_off_minor", "currency", "duration", "metadata"]
        )
        return self


class PromotionSpec(PromotionSpecProto, BillingSpec):
    """Promotion creation specification."""

    coupon_id: Optional[str] = Field(
        default=None, description="Coupon identifier associated with the promotion"
    )
    code: Optional[str] = Field(
        default=None, description="Public code used to redeem the promotion"
    )
    metadata: Mapping[str, Any] | None = Field(
        default=None, description="Metadata attached to the promotion"
    )

    @model_validator(mode="after")
    def _populate_from_payload(self) -> "PromotionSpec":
        self._apply_payload_defaults(["coupon_id", "code", "metadata"])
        return self
