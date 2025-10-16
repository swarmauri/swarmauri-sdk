"""Concrete Adyen billing provider."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence
from uuid import uuid4

from swarmauri_base.billing import (
    BalanceTransfersMixin,
    BillingProviderBase,
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
from swarmauri_core.billing import ALL_CAPABILITIES


class AdyenBillingProvider(
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
    BillingProviderBase,
):
    """Example Adyen provider returning deterministic stubbed responses."""

    CAPABILITIES = ALL_CAPABILITIES

    def _stub(self, action: str, **payload: Any) -> Mapping[str, Any]:
        return {
            "id": f"ady_{action}_{uuid4().hex[:10]}",
            "provider": "adyen",
            "action": action,
            "payload": payload,
        }

    # ---------------------------------------------------------------- Products & Prices
    def _create_product(
        self, product_spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        result = {
            "id": f"ady_prod_{uuid4().hex[:8]}",
            "provider": "adyen",
            "name": getattr(product_spec, "name", "Adyen Product"),
            "raw": self._stub("product", idempotency_key=idempotency_key),
        }
        return result

    def _create_price(
        self,
        product: Any,
        price_spec: Any,
        *,
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        result = {
            "id": f"ady_price_{uuid4().hex[:8]}",
            "product_id": getattr(product, "id", ""),
            "provider": "adyen",
            "raw": self._stub("price", idempotency_key=idempotency_key),
        }
        return result

    # ---------------------------------------------------------------- Hosted Checkout
    def _create_checkout(self, price: Any, request: Any) -> Mapping[str, Any]:
        result = {
            "id": f"ady_chk_{uuid4().hex[:10]}",
            "url": "https://checkout.adyen.example/session",
            "provider": "adyen",
            "raw": self._stub("checkout"),
        }
        return result

    # ---------------------------------------------------------------- Online Payments
    def _create_payment_intent(self, req: Any) -> Mapping[str, Any]:
        result = {
            "id": f"ady_pi_{uuid4().hex[:10]}",
            "status": "requires_action",
            "provider": "adyen",
            "raw": self._stub("payment_intent"),
        }
        return result

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> Mapping[str, Any]:
        result = {
            "id": payment_id,
            "status": "succeeded",
            "provider": "adyen",
            "raw": self._stub("capture", payment_id=payment_id),
        }
        return result

    def _cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Mapping[str, Any]:
        result = {
            "id": payment_id,
            "status": "canceled",
            "provider": "adyen",
            "raw": self._stub("cancel", payment_id=payment_id, reason=reason),
        }
        return result

    # ---------------------------------------------------------------- Subscriptions
    def _create_subscription(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        result = {
            "subscription_id": f"ady_sub_{uuid4().hex[:8]}",
            "status": "active",
            "provider": "adyen",
            "raw": self._stub("subscription_create"),
        }
        return result

    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        result = {
            "subscription_id": subscription_id,
            "status": "canceled",
            "provider": "adyen",
            "raw": self._stub("subscription_cancel"),
        }
        return result

    # ---------------------------------------------------------------- Invoicing
    def _create_invoice(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        result = {
            "invoice_id": f"ady_inv_{uuid4().hex[:8]}",
            "status": "draft",
            "provider": "adyen",
            "raw": self._stub("invoice_create"),
        }
        return result

    def _finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        result = {
            "invoice_id": invoice_id,
            "status": "finalized",
            "provider": "adyen",
            "raw": self._stub("invoice_finalize"),
        }
        return result

    def _void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        result = {
            "invoice_id": invoice_id,
            "status": "void",
            "provider": "adyen",
            "raw": self._stub("invoice_void"),
        }
        return result

    def _mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        result = {
            "invoice_id": invoice_id,
            "status": "uncollectible",
            "provider": "adyen",
            "raw": self._stub("invoice_uncollectible"),
        }
        return result

    # ---------------------------------------------------------------- Marketplace
    def _create_split(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        result = {
            "split": self._stub("split_create"),
            "provider": "adyen",
        }
        return result

    def _charge_with_split(
        self,
        amount_minor: int,
        currency: str,
        *,
        split_code_or_params: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        result = {
            "payment_id": f"ady_pay_{uuid4().hex[:10]}",
            "status": "processing",
            "provider": "adyen",
            "raw": self._stub("charge_split"),
        }
        return result

    # ---------------------------------------------------------------- Risk
    def _verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        return True

    def _list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        disputes = [
            {
                "id": f"ady_dispute_{uuid4().hex[:8]}",
                "provider": "adyen",
                "status": "in_progress",
            }
        ]
        return disputes

    # ---------------------------------------------------------------- Refunds
    def _create_refund(
        self, payment: Any, req: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        result = self._stub("refund_create", idempotency_key=idempotency_key)
        return result

    def _get_refund(self, refund_id: str) -> Mapping[str, Any]:
        result = self._stub("refund_get", refund_id=refund_id)
        return result

    # ---------------------------------------------------------------- Customers
    def _create_customer(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        result = {
            "id": f"ady_cus_{uuid4().hex[:8]}",
            "provider": "adyen",
            "raw": self._stub("customer_create"),
        }
        return result

    def _get_customer(self, customer_id: str) -> Mapping[str, Any]:
        result = {
            "id": customer_id,
            "provider": "adyen",
            "raw": self._stub("customer_get"),
        }
        return result

    def _attach_payment_method_to_customer(
        self, customer: Any, pm: Any
    ) -> Mapping[str, Any]:
        result = self._stub(
            "customer_attach_pm",
            customer_id=getattr(customer, "id", None),
            payment_method_id=getattr(pm, "id", None),
        )
        return result

    # ---------------------------------------------------------------- Payment Methods
    def _create_payment_method(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        result = {
            "id": f"ady_pm_{uuid4().hex[:8]}",
            "provider": "adyen",
            "raw": self._stub("payment_method_create"),
        }
        return result

    def _detach_payment_method(self, payment_method_id: str) -> Mapping[str, Any]:
        result = self._stub(
            "payment_method_detach", payment_method_id=payment_method_id
        )
        return result

    def _list_payment_methods(
        self,
        customer: Any,
        *,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> Sequence[Mapping[str, Any]]:
        methods = [
            {
                "id": f"ady_pm_{uuid4().hex[:8]}",
                "provider": "adyen",
                "raw": self._stub("payment_method"),
            }
        ]
        return methods

    # ---------------------------------------------------------------- Payouts
    def _create_payout(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        result = self._stub("payout_create", idempotency_key=idempotency_key)
        return result

    # ---------------------------------------------------------------- Balance & Transfers
    def _get_balance(self) -> Mapping[str, Any]:
        result = {
            "snapshot_id": f"ady_bal_{uuid4().hex[:6]}",
            "provider": "adyen",
            "raw": self._stub("balance"),
        }
        return result

    def _create_transfer(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        result = self._stub("transfer_create", idempotency_key=idempotency_key)
        return result

    # ---------------------------------------------------------------- Reports
    def _create_report(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        result = self._stub("report_create", idempotency_key=idempotency_key)
        return result

    # ---------------------------------------------------------------- Webhooks
    def _parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> Mapping[str, Any]:
        result = {
            "event_id": f"ady_evt_{uuid4().hex[:8]}",
            "provider": "adyen",
            "type": "AUTHORISATION",
            "raw": self._stub("event"),
        }
        return result

    # ---------------------------------------------------------------- Promotions
    def _create_coupon(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        result = self._stub("coupon_create", idempotency_key=idempotency_key)
        return result

    def _create_promotion(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        result = self._stub("promotion_create", idempotency_key=idempotency_key)
        return result


__all__ = ["AdyenBillingProvider"]
