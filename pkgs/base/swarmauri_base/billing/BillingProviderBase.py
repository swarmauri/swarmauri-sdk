"""Base provider implementation composing all billing mixins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, FrozenSet, Mapping, Optional, Sequence, Tuple, Type

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.billing import (
    ALL_API_STRATEGIES,
    ALL_CAPABILITIES,
    Capability,
    IBillingProvider,
    Operation,
)
from swarmauri_core.billing.protos import (
    BalanceRefProto,
    CheckoutIntentProto,
    CheckoutReqProto,
    CustomerRefProto,
    CustomerSpecProto,
    InvoiceSpecProto,
    PaymentIntentReqProto,
    PaymentMethodRefProto,
    PaymentMethodSpecProto,
    PaymentRefProto,
    PayoutReqProto,
    PriceRefProto,
    PriceSpecProto,
    ProductRefProto,
    ProductSpecProto,
    RefundReqProto,
    ReportReqProto,
    SplitSpecProto,
    SubscriptionSpecProto,
    TransferReqProto,
    WebhookEventProto,
)

from .mixins import (
    BalanceTransfersMixin,
    CustomersMixin,
    HostedCheckoutMixin,
    InvoicingMixin,
    MarketplaceMixin,
    OnlinePaymentsMixin,
    PaymentMethodsMixin,
    PayoutsMixin,
    ProductsPricesMixin,
    PromotionsMixin,
    RefundsMixin,
    ReportsMixin,
    RiskMixin,
    SubscriptionsMixin,
    WebhooksMixin,
)


class BillingProviderBase(
    ProductsPricesMixin,
    HostedCheckoutMixin,
    OnlinePaymentsMixin,
    SubscriptionsMixin,
    InvoicingMixin,
    MarketplaceMixin,
    RiskMixin,
    RefundsMixin,
    CustomersMixin,
    PaymentMethodsMixin,
    PayoutsMixin,
    BalanceTransfersMixin,
    ReportsMixin,
    WebhooksMixin,
    PromotionsMixin,
    ComponentBase,
    IBillingProvider,
    ABC,
):
    """Base class for billing providers that delegates to mixin dispatch."""

    CAPABILITIES: ClassVar[FrozenSet[Capability]] = ALL_CAPABILITIES

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    api_key: str = Field(
        ..., description="API key used to authenticate with the billing provider"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Optional base URL override for the provider API.",
    )
    timeout: float = Field(
        default=30.0,
        description="Timeout in seconds for provider requests.",
    )

    resource: str = Field(default="BillingProvider")

    @abstractmethod
    def _dispatch(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str],
    ) -> Any:
        """Concrete providers must implement the dispatch method."""

    def _op(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> Any:
        self._pre(operation.value, payload=payload, idempotency_key=idempotency_key)
        result = self._dispatch(operation, payload, idempotency_key=idempotency_key)
        self._post(operation.value, result)
        return result

    # Products & Prices -------------------------------------------------
    def _create_product(
        self, product_spec: ProductSpecProto, *, idempotency_key: str
    ) -> ProductRefProto | Mapping[str, Any]:
        return self._op(
            Operation.CREATE_PRODUCT,
            {"product_spec": product_spec},
            idempotency_key=idempotency_key,
        )

    def _create_price(
        self,
        product: ProductRefProto,
        price_spec: PriceSpecProto,
        *,
        idempotency_key: str,
    ) -> PriceRefProto | Mapping[str, Any]:
        return self._op(
            Operation.CREATE_PRICE,
            {"product": product, "price_spec": price_spec},
            idempotency_key=idempotency_key,
        )

    # Hosted Checkout ---------------------------------------------------
    def _create_checkout(
        self, price: PriceRefProto, request: CheckoutReqProto
    ) -> CheckoutIntentProto | Mapping[str, Any]:
        return self._op(
            Operation.CREATE_CHECKOUT,
            {"price": price, "request": request},
        )

    # Online Payments ---------------------------------------------------
    def _create_payment_intent(
        self, req: PaymentIntentReqProto
    ) -> PaymentRefProto | Mapping[str, Any]:
        return self._op(Operation.CREATE_PAYMENT_INTENT, {"req": req})

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> PaymentRefProto | Mapping[str, Any]:
        return self._op(
            Operation.CAPTURE_PAYMENT,
            {"payment_id": payment_id},
            idempotency_key=idempotency_key,
        )

    def _cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentRefProto | Mapping[str, Any]:
        return self._op(
            Operation.CANCEL_PAYMENT,
            {"payment_id": payment_id, "reason": reason},
            idempotency_key=idempotency_key,
        )

    # Subscriptions -----------------------------------------------------
    def _create_subscription(
        self, spec: SubscriptionSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return self._op(
            Operation.CREATE_SUBSCRIPTION,
            {"spec": spec},
            idempotency_key=idempotency_key,
        )

    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        return self._op(
            Operation.CANCEL_SUBSCRIPTION,
            {"subscription_id": subscription_id, "at_period_end": at_period_end},
        )

    # Invoicing ---------------------------------------------------------
    def _create_invoice(
        self, spec: InvoiceSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return self._op(
            Operation.CREATE_INVOICE,
            {"spec": spec},
            idempotency_key=idempotency_key,
        )

    def _finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        return self._op(Operation.FINALIZE_INVOICE, {"invoice_id": invoice_id})

    def _void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        return self._op(Operation.VOID_INVOICE, {"invoice_id": invoice_id})

    def _mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        return self._op(Operation.MARK_UNCOLLECTIBLE, {"invoice_id": invoice_id})

    # Marketplace -------------------------------------------------------
    def _create_split(
        self, spec: SplitSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return self._op(
            Operation.CREATE_SPLIT,
            {"spec": spec},
            idempotency_key=idempotency_key,
        )

    def _charge_with_split(
        self,
        amount_minor: int,
        currency: str,
        *,
        split_code_or_params: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        payload = {
            "amount_minor": amount_minor,
            "currency": currency,
            "split": split_code_or_params,
        }
        return self._op(
            Operation.CHARGE_WITH_SPLIT,
            payload,
            idempotency_key=idempotency_key,
        )

    # Risk --------------------------------------------------------------
    def _verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool | Mapping[str, Any]:
        return self._op(
            Operation.VERIFY_WEBHOOK_SIGNATURE,
            {"raw_body": raw_body, "headers": headers, "secret": secret},
        )

    def _list_disputes(
        self, *, limit: int = 50
    ) -> Sequence[Mapping[str, Any]] | Mapping[str, Any] | None:
        return self._op(Operation.LIST_DISPUTES, {"limit": limit})

    # Refunds -----------------------------------------------------------
    def _create_refund(
        self, payment: PaymentRefProto, req: RefundReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return self._op(
            Operation.CREATE_REFUND,
            {"payment": payment, "req": req},
            idempotency_key=idempotency_key,
        )

    def _get_refund(self, refund_id: str) -> Mapping[str, Any]:
        return self._op(Operation.GET_REFUND, {"refund_id": refund_id})

    # Customers ---------------------------------------------------------
    def _create_customer(
        self, spec: CustomerSpecProto, *, idempotency_key: str
    ) -> CustomerRefProto | Mapping[str, Any]:
        return self._op(
            Operation.CREATE_CUSTOMER,
            {"spec": spec},
            idempotency_key=idempotency_key,
        )

    def _get_customer(self, customer_id: str) -> CustomerRefProto | Mapping[str, Any]:
        return self._op(Operation.GET_CUSTOMER, {"customer_id": customer_id})

    def _attach_payment_method_to_customer(
        self, customer: CustomerRefProto, pm: PaymentMethodRefProto
    ) -> Mapping[str, Any]:
        return self._op(
            Operation.ATTACH_PM_TO_CUSTOMER,
            {"customer": customer, "payment_method": pm},
        )

    # Payment Methods ---------------------------------------------------
    def _create_payment_method(
        self, spec: PaymentMethodSpecProto, *, idempotency_key: str
    ) -> PaymentMethodRefProto | Mapping[str, Any]:
        return self._op(
            Operation.CREATE_PAYMENT_METHOD,
            {"spec": spec},
            idempotency_key=idempotency_key,
        )

    def _detach_payment_method(self, payment_method_id: str) -> Mapping[str, Any]:
        return self._op(
            Operation.DETACH_PAYMENT_METHOD,
            {"payment_method_id": payment_method_id},
        )

    def _list_payment_methods(
        self,
        customer: CustomerRefProto,
        *,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> (
        Sequence[PaymentMethodRefProto]
        | Sequence[Mapping[str, Any]]
        | Mapping[str, Any]
        | None
    ):
        return self._op(
            Operation.LIST_PAYMENT_METHODS,
            {"customer": customer, "type": type, "limit": limit},
        )

    # Payouts -----------------------------------------------------------
    def _create_payout(
        self, req: PayoutReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return self._op(
            Operation.CREATE_PAYOUT,
            {"req": req},
            idempotency_key=idempotency_key,
        )

    # Balance & Transfers ----------------------------------------------
    def _get_balance(self) -> BalanceRefProto | Mapping[str, Any]:
        return self._op(Operation.GET_BALANCE, {})

    def _create_transfer(
        self, req: TransferReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return self._op(
            Operation.CREATE_TRANSFER,
            {"req": req},
            idempotency_key=idempotency_key,
        )

    # Reports -----------------------------------------------------------
    def _create_report(
        self, req: ReportReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return self._op(
            Operation.CREATE_REPORT,
            {"req": req},
            idempotency_key=idempotency_key,
        )

    # Webhooks ----------------------------------------------------------
    def _parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> WebhookEventProto | Mapping[str, Any]:
        return self._op(
            Operation.PARSE_EVENT,
            {"raw_body": raw_body, "headers": headers},
        )

    # Hooks -----------------------------------------------------------------
    def _pre(self, action: str, **metadata: Any) -> None:
        """Hook executed before delegating to ``_dispatch``."""

        logger = getattr(self, "logger", None)
        if logger is not None:
            logger.debug("billing.%s.pre", action, extra={"payload": metadata})

    def _post(self, action: str, response: Any) -> None:
        """Hook executed after ``_dispatch`` returns."""

        logger = getattr(self, "logger", None)
        if logger is not None:
            logger.debug("billing.%s.post", action, extra={"response": response})

    @property
    def capabilities(self) -> FrozenSet[Capability]:
        return self.CAPABILITIES

    @property
    def api_strategies(self) -> Tuple[Type[Any], ...]:
        return ALL_API_STRATEGIES
