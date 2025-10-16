"""Interfaces and opaque protocol types for billing providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Final, FrozenSet, Mapping, Optional, Sequence, Tuple, Type


# ---- Domain "protos" (opaque shapes used for typed signatures only)


class ProductSpecProto(ABC):
    """Opaque product specification passed to providers."""


class PriceSpecProto(ABC):
    """Opaque price specification passed to providers."""


class CheckoutReqProto(ABC):
    """Opaque hosted checkout request passed to providers."""


class ProductRefProto(ABC):
    """Opaque product reference returned by providers."""


class PriceRefProto(ABC):
    """Opaque price reference returned by providers."""


class CheckoutIntentProto(ABC):
    """Opaque checkout intent returned by providers."""


class PaymentIntentReqProto(ABC):
    """Opaque payment intent request passed to providers."""


class PaymentRefProto(ABC):
    """Opaque payment reference returned by providers."""


class SubscriptionSpecProto(ABC):
    """Opaque subscription specification passed to providers."""


class InvoiceSpecProto(ABC):
    """Opaque invoice specification passed to providers."""


class SplitSpecProto(ABC):
    """Opaque marketplace split specification passed to providers."""


class RefundReqProto(ABC):
    """Opaque refund request passed to providers."""


class CustomerSpecProto(ABC):
    """Opaque customer specification passed to providers."""


class CustomerRefProto(ABC):
    """Opaque customer reference returned by providers."""


class PaymentMethodSpecProto(ABC):
    """Opaque payment method specification passed to providers."""


class PaymentMethodRefProto(ABC):
    """Opaque payment method reference returned by providers."""


class PayoutReqProto(ABC):
    """Opaque payout request passed to providers."""


class TransferReqProto(ABC):
    """Opaque transfer request passed to providers."""


class BalanceRefProto(ABC):
    """Opaque balance snapshot returned by providers."""


class ReportReqProto(ABC):
    """Opaque report request passed to providers."""


class WebhookEventProto(ABC):
    """Opaque webhook event returned by providers."""


class CouponSpecProto(ABC):
    """Opaque coupon specification passed to providers."""


class PromotionSpecProto(ABC):
    """Opaque promotion specification passed to providers."""


# ---- Strategy interfaces (signatures only; no implementation)


class IProductsPrices(ABC):
    """Operations for creating catalog products and prices."""

    @abstractmethod
    def create_product(
        self, product_spec: ProductSpecProto, *, idempotency_key: str
    ) -> ProductRefProto:
        """Create a product in the remote provider."""

    @abstractmethod
    def create_price(
        self,
        product: ProductRefProto,
        price_spec: PriceSpecProto,
        *,
        idempotency_key: str,
    ) -> PriceRefProto:
        """Create a price for the given product in the remote provider."""


class IHostedCheckout(ABC):
    """Operations for hosted checkout experiences."""

    @abstractmethod
    def create_checkout(
        self, price: PriceRefProto, request: CheckoutReqProto
    ) -> CheckoutIntentProto:
        """Create a hosted checkout session."""


class IOnlinePayments(ABC):
    """Operations for online payment intents."""

    @abstractmethod
    def create_payment_intent(self, req: PaymentIntentReqProto) -> PaymentRefProto:
        """Create a payment intent."""

    @abstractmethod
    def capture_payment(
        self,
        payment_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> PaymentRefProto:
        """Capture a previously created payment intent."""

    @abstractmethod
    def cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentRefProto:
        """Cancel a previously created payment intent."""


class ISubscriptions(ABC):
    """Operations for managing recurring subscriptions."""

    @abstractmethod
    def create_subscription(
        self,
        spec: SubscriptionSpecProto,
        *,
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        """Create a subscription."""

    @abstractmethod
    def cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        """Cancel or schedule cancellation of a subscription."""


class IInvoicing(ABC):
    """Operations for managing invoices."""

    @abstractmethod
    def create_invoice(
        self, spec: InvoiceSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create an invoice."""

    @abstractmethod
    def finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        """Finalize a draft invoice."""

    @abstractmethod
    def void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        """Void an invoice."""

    @abstractmethod
    def mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        """Mark an invoice as uncollectible."""


class IMarketplace(ABC):
    """Operations for marketplace style split payments."""

    @abstractmethod
    def create_split(
        self, spec: SplitSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create or register a marketplace split configuration."""

    @abstractmethod
    def charge_with_split(
        self,
        amount_minor: int,
        currency: str,
        *,
        split_code_or_params: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        """Charge using a split configuration."""


class IRisk(ABC):
    """Operations for risk and dispute handling."""

    @abstractmethod
    def verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        """Verify the authenticity of a webhook payload."""

    @abstractmethod
    def list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        """List disputes for the account."""


class IRefunds(ABC):
    """Operations for processing refunds."""

    @abstractmethod
    def create_refund(
        self,
        payment: PaymentRefProto,
        req: RefundReqProto,
        *,
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        """Create a refund against a payment."""

    @abstractmethod
    def get_refund(self, refund_id: str) -> Mapping[str, Any]:
        """Fetch a refund by identifier."""


class ICustomers(ABC):
    """Operations for managing customers."""

    @abstractmethod
    def create_customer(
        self, spec: CustomerSpecProto, *, idempotency_key: str
    ) -> CustomerRefProto:
        """Create a customer."""

    @abstractmethod
    def get_customer(self, customer_id: str) -> CustomerRefProto:
        """Fetch a customer by identifier."""

    @abstractmethod
    def attach_payment_method_to_customer(
        self,
        customer: CustomerRefProto,
        pm: PaymentMethodRefProto,
    ) -> Mapping[str, Any]:
        """Attach a payment method to the customer."""


class IPaymentMethods(ABC):
    """Operations for managing payment methods."""

    @abstractmethod
    def create_payment_method(
        self,
        spec: PaymentMethodSpecProto,
        *,
        idempotency_key: str,
    ) -> PaymentMethodRefProto:
        """Create a payment method."""

    @abstractmethod
    def detach_payment_method(self, payment_method_id: str) -> Mapping[str, Any]:
        """Detach a payment method from a customer."""

    @abstractmethod
    def list_payment_methods(
        self,
        customer: CustomerRefProto,
        *,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> Sequence[PaymentMethodRefProto]:
        """List payment methods for a customer."""


class IPayouts(ABC):
    """Operations for direct payouts."""

    @abstractmethod
    def create_payout(
        self, req: PayoutReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a payout."""


class IBalanceTransfers(ABC):
    """Operations for account balance and transfers."""

    @abstractmethod
    def get_balance(self) -> BalanceRefProto:
        """Fetch the current balance snapshot."""

    @abstractmethod
    def create_transfer(
        self, req: TransferReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a transfer between accounts."""


class IReports(ABC):
    """Operations for reporting jobs."""

    @abstractmethod
    def create_report(
        self, req: ReportReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a report job."""


class IWebhooks(ABC):
    """Operations for webhook ingestion."""

    @abstractmethod
    def parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> WebhookEventProto:
        """Parse a webhook payload into a provider specific event."""


class IPromotions(ABC):
    """Operations for coupons and promotions."""

    @abstractmethod
    def create_coupon(
        self, spec: CouponSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a coupon."""

    @abstractmethod
    def create_promotion(
        self, spec: PromotionSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a promotion."""


# ---- Provider capability & operation metadata


class Capability(Enum):
    """Capabilities that a billing provider may expose."""

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


class Operation(Enum):
    """Concrete provider operations routed through the dispatch layer."""

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


ALL_CAPABILITIES: Final[FrozenSet[Capability]] = frozenset(
    capability for capability in Capability
)


# ---- Indexes for discovery / introspection


ALL_API_STRATEGIES: Tuple[Type[ABC], ...] = (
    IProductsPrices,
    IHostedCheckout,
    IOnlinePayments,
    ISubscriptions,
    IInvoicing,
    IMarketplace,
    IRisk,
    IRefunds,
    ICustomers,
    IPaymentMethods,
    IPayouts,
    IBalanceTransfers,
    IReports,
    IWebhooks,
    IPromotions,
)


class IBillingProvider(ABC):
    """Common contract implemented by every billing provider."""

    @abstractmethod
    def _dispatch(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str],
    ) -> Any:
        """Dispatch a provider specific API call."""

    @property
    @abstractmethod
    def capabilities(self) -> FrozenSet[Capability]:
        """The set of capabilities supported by the provider."""

    @property
    @abstractmethod
    def api_strategies(self) -> Tuple[Type[Any], ...]:
        """Strategy interfaces implemented by the provider."""


__all__ = [
    "ALL_API_STRATEGIES",
    "ALL_CAPABILITIES",
    "Capability",
    "CheckoutIntentProto",
    "CheckoutReqProto",
    "CustomerRefProto",
    "CustomerSpecProto",
    "IBalanceTransfers",
    "IBillingProvider",
    "ICustomers",
    "IHostedCheckout",
    "IMarketplace",
    "IInvoicing",
    "IOnlinePayments",
    "IPaymentMethods",
    "IPayouts",
    "IPromotions",
    "IProductsPrices",
    "IRefunds",
    "IReports",
    "IRisk",
    "ISubscriptions",
    "IWebhooks",
    "InvoiceSpecProto",
    "Operation",
    "PaymentIntentReqProto",
    "PaymentMethodRefProto",
    "PaymentMethodSpecProto",
    "PaymentRefProto",
    "PayoutReqProto",
    "PriceRefProto",
    "PriceSpecProto",
    "ProductRefProto",
    "ProductSpecProto",
    "PromotionSpecProto",
    "RefundReqProto",
    "ReportReqProto",
    "SplitSpecProto",
    "SubscriptionSpecProto",
    "TransferReqProto",
    "WebhookEventProto",
]
