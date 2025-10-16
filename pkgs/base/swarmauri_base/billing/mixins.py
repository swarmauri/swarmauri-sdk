"""Billing provider mixins implementing the strategy interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, Sequence, cast

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing.interfaces import (
    ALL_API_STRATEGIES,
    CheckoutIntentProto,
    CheckoutReqProto,
    ICustomers,
    IHostedCheckout,
    IInvoicing,
    IMarketplace,
    IOnlinePayments,
    IPaymentMethods,
    IPayouts,
    IPromotions,
    IProductsPrices,
    IRefunds,
    IReports,
    IRisk,
    ISubscriptions,
    IWebhooks,
    IBalanceTransfers,
    InvoiceSpecProto,
    Operation,
    PaymentIntentReqProto,
    PaymentMethodRefProto,
    PaymentMethodSpecProto,
    PaymentRefProto,
    PayoutReqProto,
    PriceSpecProto,
    PriceRefProto,
    ProductRefProto,
    ProductSpecProto,
    PromotionSpecProto,
    CustomerRefProto,
    RefundReqProto,
    ReportReqProto,
    SplitSpecProto,
    SubscriptionSpecProto,
    TransferReqProto,
    CouponSpecProto,
    CustomerSpecProto,
)

from .models import (
    BalanceRef,
    CheckoutIntent,
    CustomerRef,
    PaymentMethodRef,
    PaymentRef,
    PriceRef,
    ProductRef,
    WebhookEvent,
)


class _BillingMixinBase(BaseModel, ABC):
    """Base class for mixins, providing the shared dispatch helper."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore")

    @abstractmethod
    def _op(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> Any:
        """Route the call to the provider specific dispatch implementation."""

    def _require_idempotency(self, key: Optional[str]) -> None:
        if not key or not key.strip():
            raise ValueError("idempotency_key is required and must be non-empty.")


class ProductsPricesMixin(IProductsPrices, _BillingMixinBase):
    """Implements the product and price strategy by delegating to :meth:`_op`."""

    def create_product(
        self, product_spec: ProductSpecProto, *, idempotency_key: str
    ) -> ProductRefProto:
        self._require_idempotency(idempotency_key)
        raw = cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_PRODUCT,
                {"product_spec": product_spec},
                idempotency_key=idempotency_key,
            ),
        )
        return ProductRef(
            id=str(raw.get("id", "")), provider=str(raw.get("provider", "")), raw=raw
        )

    def create_price(
        self,
        product: ProductRefProto,
        price_spec: PriceSpecProto,
        *,
        idempotency_key: str,
    ) -> PriceRefProto:
        self._require_idempotency(idempotency_key)
        raw = cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_PRICE,
                {"product": product, "price_spec": price_spec},
                idempotency_key=idempotency_key,
            ),
        )
        return PriceRef(
            id=str(raw.get("id", "")),
            provider=str(raw.get("provider", "")),
            product_id=getattr(product, "id", None),
            raw=raw,
        )


class HostedCheckoutMixin(IHostedCheckout, _BillingMixinBase):
    """Hosted checkout implementation."""

    def create_checkout(
        self, price: PriceRefProto, request: CheckoutReqProto
    ) -> CheckoutIntentProto:
        raw = cast(
            Mapping[str, Any],
            self._op(Operation.CREATE_CHECKOUT, {"price": price, "request": request}),
        )
        return CheckoutIntent(
            id=str(raw.get("id", "")),
            provider=str(raw.get("provider", "")),
            url=raw.get("url"),
            client_secret=raw.get("client_secret"),
            raw=raw,
        )


class OnlinePaymentsMixin(IOnlinePayments, _BillingMixinBase):
    """Online payment intent implementation."""

    def create_payment_intent(self, req: PaymentIntentReqProto) -> PaymentRefProto:
        raw = cast(
            Mapping[str, Any], self._op(Operation.CREATE_PAYMENT_INTENT, {"req": req})
        )
        return PaymentRef(
            id=str(raw.get("id", "")),
            provider=str(raw.get("provider", "")),
            status=raw.get("status"),
            raw=raw,
        )

    def capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> PaymentRefProto:
        raw = cast(
            Mapping[str, Any],
            self._op(
                Operation.CAPTURE_PAYMENT,
                {"payment_id": payment_id},
                idempotency_key=idempotency_key,
            ),
        )
        return PaymentRef(
            id=str(raw.get("id", "")),
            provider=str(raw.get("provider", "")),
            status=raw.get("status"),
            raw=raw,
        )

    def cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentRefProto:
        raw = cast(
            Mapping[str, Any],
            self._op(
                Operation.CANCEL_PAYMENT,
                {"payment_id": payment_id, "reason": reason},
                idempotency_key=idempotency_key,
            ),
        )
        return PaymentRef(
            id=str(raw.get("id", "")),
            provider=str(raw.get("provider", "")),
            status=raw.get("status"),
            raw=raw,
        )


class SubscriptionsMixin(ISubscriptions, _BillingMixinBase):
    """Subscription management implementation."""

    def create_subscription(
        self, spec: SubscriptionSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_SUBSCRIPTION,
                {"spec": spec},
                idempotency_key=idempotency_key,
            ),
        )

    def cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.CANCEL_SUBSCRIPTION,
                {"subscription_id": subscription_id, "at_period_end": at_period_end},
            ),
        )


class InvoicingMixin(IInvoicing, _BillingMixinBase):
    """Invoice management implementation."""

    def create_invoice(
        self, spec: InvoiceSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_INVOICE,
                {"spec": spec},
                idempotency_key=idempotency_key,
            ),
        )

    def finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        return cast(
            Mapping[str, Any],
            self._op(Operation.FINALIZE_INVOICE, {"invoice_id": invoice_id}),
        )

    def void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        return cast(
            Mapping[str, Any],
            self._op(Operation.VOID_INVOICE, {"invoice_id": invoice_id}),
        )

    def mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        return cast(
            Mapping[str, Any],
            self._op(Operation.MARK_UNCOLLECTIBLE, {"invoice_id": invoice_id}),
        )


class MarketplaceMixin(IMarketplace, _BillingMixinBase):
    """Marketplace split operations."""

    def create_split(
        self, spec: SplitSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_SPLIT, {"spec": spec}, idempotency_key=idempotency_key
            ),
        )

    def charge_with_split(
        self,
        amount_minor: int,
        currency: str,
        *,
        split_code_or_params: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        payload = {
            "amount_minor": amount_minor,
            "currency": currency,
            "split": split_code_or_params,
        }
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.CHARGE_WITH_SPLIT, payload, idempotency_key=idempotency_key
            ),
        )


class RiskMixin(IRisk, _BillingMixinBase):
    """Risk related helpers."""

    def verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        return bool(
            self._op(
                Operation.VERIFY_WEBHOOK_SIGNATURE,
                {"raw_body": raw_body, "headers": headers, "secret": secret},
            )
        )

    def list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        return cast(
            Sequence[Mapping[str, Any]],
            self._op(Operation.LIST_DISPUTES, {"limit": limit}),
        )


class RefundsMixin(IRefunds, _BillingMixinBase):
    """Refund operations."""

    def create_refund(
        self,
        payment: PaymentRefProto,
        req: RefundReqProto,
        *,
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_REFUND,
                {"payment": payment, "req": req},
                idempotency_key=idempotency_key,
            ),
        )

    def get_refund(self, refund_id: str) -> Mapping[str, Any]:
        return cast(
            Mapping[str, Any], self._op(Operation.GET_REFUND, {"refund_id": refund_id})
        )


class CustomersMixin(ICustomers, _BillingMixinBase):
    """Customer operations."""

    def create_customer(
        self, spec: CustomerSpecProto, *, idempotency_key: str
    ) -> CustomerRefProto:
        self._require_idempotency(idempotency_key)
        raw = cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_CUSTOMER,
                {"spec": spec},
                idempotency_key=idempotency_key,
            ),
        )
        return CustomerRef(
            id=str(raw.get("id", "")), provider=str(raw.get("provider", "")), raw=raw
        )

    def get_customer(self, customer_id: str) -> CustomerRefProto:
        raw = cast(
            Mapping[str, Any],
            self._op(Operation.GET_CUSTOMER, {"customer_id": customer_id}),
        )
        return CustomerRef(
            id=str(raw.get("id", "")), provider=str(raw.get("provider", "")), raw=raw
        )

    def attach_payment_method_to_customer(
        self,
        customer: CustomerRefProto,
        pm: PaymentMethodRefProto,
    ) -> Mapping[str, Any]:
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.ATTACH_PM_TO_CUSTOMER,
                {"customer": customer, "payment_method": pm},
            ),
        )


class PaymentMethodsMixin(IPaymentMethods, _BillingMixinBase):
    """Payment method operations."""

    def create_payment_method(
        self,
        spec: PaymentMethodSpecProto,
        *,
        idempotency_key: str,
    ) -> PaymentMethodRefProto:
        self._require_idempotency(idempotency_key)
        raw = cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_PAYMENT_METHOD,
                {"spec": spec},
                idempotency_key=idempotency_key,
            ),
        )
        return PaymentMethodRef(
            id=str(raw.get("id", "")), provider=str(raw.get("provider", "")), raw=raw
        )

    def detach_payment_method(self, payment_method_id: str) -> Mapping[str, Any]:
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.DETACH_PAYMENT_METHOD,
                {"payment_method_id": payment_method_id},
            ),
        )

    def list_payment_methods(
        self,
        customer: CustomerRefProto,
        *,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> Sequence[PaymentMethodRefProto]:
        raws = cast(
            Sequence[Mapping[str, Any]],
            self._op(
                Operation.LIST_PAYMENT_METHODS,
                {"customer": customer, "type": type, "limit": limit},
            ),
        )
        return tuple(
            PaymentMethodRef(
                id=str(r.get("id", "")), provider=str(r.get("provider", "")), raw=r
            )
            for r in raws
        )


class PayoutsMixin(IPayouts, _BillingMixinBase):
    """Payout operations."""

    def create_payout(
        self, req: PayoutReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_PAYOUT, {"req": req}, idempotency_key=idempotency_key
            ),
        )


class BalanceTransfersMixin(IBalanceTransfers, _BillingMixinBase):
    """Balance and transfer operations."""

    def get_balance(self) -> BalanceRef:
        raw = cast(Mapping[str, Any], self._op(Operation.GET_BALANCE, {}))
        return BalanceRef(
            snapshot_id=str(raw.get("snapshot_id", "")),
            provider=str(raw.get("provider", "")),
            raw=raw,
        )

    def create_transfer(
        self, req: TransferReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_TRANSFER, {"req": req}, idempotency_key=idempotency_key
            ),
        )


class ReportsMixin(IReports, _BillingMixinBase):
    """Reporting operations."""

    def create_report(
        self, req: ReportReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_REPORT, {"req": req}, idempotency_key=idempotency_key
            ),
        )


class WebhooksMixin(IWebhooks, _BillingMixinBase):
    """Webhook helper operations."""

    def parse_event(self, raw_body: bytes, headers: Mapping[str, str]) -> WebhookEvent:
        raw = cast(
            Mapping[str, Any],
            self._op(Operation.PARSE_EVENT, {"raw_body": raw_body, "headers": headers}),
        )
        return WebhookEvent(
            event_id=str(raw.get("event_id", "")),
            provider=str(raw.get("provider", "")),
            raw=raw,
        )


class PromotionsMixin(IPromotions, _BillingMixinBase):
    """Coupon and promotion operations."""

    def create_coupon(
        self, spec: CouponSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_COUPON, {"spec": spec}, idempotency_key=idempotency_key
            ),
        )

    def create_promotion(
        self, spec: PromotionSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return cast(
            Mapping[str, Any],
            self._op(
                Operation.CREATE_PROMOTION,
                {"spec": spec},
                idempotency_key=idempotency_key,
            ),
        )


__all__ = [
    "ALL_API_STRATEGIES",
    "BalanceTransfersMixin",
    "CustomersMixin",
    "HostedCheckoutMixin",
    "InvoicingMixin",
    "MarketplaceMixin",
    "OnlinePaymentsMixin",
    "PaymentMethodsMixin",
    "PayoutsMixin",
    "ProductsPricesMixin",
    "PromotionsMixin",
    "RefundsMixin",
    "ReportsMixin",
    "RiskMixin",
    "SubscriptionsMixin",
    "WebhooksMixin",
]
