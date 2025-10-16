"""Mock billing provider used in tests and examples."""

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


class MockBillingProvider(
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
    """Deterministic mock provider suitable for unit tests."""

    CAPABILITIES = ALL_CAPABILITIES

    def _stub(self, action: str, **payload: Any) -> Mapping[str, Any]:
        return {
            "id": f"mock_{action}_{uuid4().hex[:10]}",
            "provider": "mock",
            "action": action,
            "payload": payload,
        }

    # Implement methods similarly to Adyen but with mock names -----------------
    def _create_product(
        self, product_spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._pre("create_product", idempotency_key=idempotency_key)
        result = {
            "id": f"mock_prod_{uuid4().hex[:6]}",
            "provider": "mock",
            "raw": self._stub("product"),
        }
        self._post("create_product", result)
        return result

    def _create_price(
        self,
        product: Any,
        price_spec: Any,
        *,
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        self._pre("create_price", product=getattr(product, "id", None))
        result = {
            "id": f"mock_price_{uuid4().hex[:6]}",
            "product_id": getattr(product, "id", ""),
            "provider": "mock",
            "raw": self._stub("price"),
        }
        self._post("create_price", result)
        return result

    def _create_checkout(self, price: Any, request: Any) -> Mapping[str, Any]:
        self._pre("create_checkout", price=getattr(price, "id", None))
        result = {
            "id": f"mock_chk_{uuid4().hex[:8]}",
            "url": "https://mock.example/checkout",
            "provider": "mock",
            "raw": self._stub("checkout"),
        }
        self._post("create_checkout", result)
        return result

    def _create_payment_intent(self, req: Any) -> Mapping[str, Any]:
        self._pre("create_payment_intent")
        result = {
            "id": f"mock_pi_{uuid4().hex[:8]}",
            "status": "requires_confirmation",
            "provider": "mock",
            "raw": self._stub("payment_intent"),
        }
        self._post("create_payment_intent", result)
        return result

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> Mapping[str, Any]:
        self._pre("capture_payment", payment_id=payment_id)
        result = {
            "id": payment_id,
            "status": "succeeded",
            "provider": "mock",
            "raw": self._stub("capture"),
        }
        self._post("capture_payment", result)
        return result

    def _cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Mapping[str, Any]:
        self._pre("cancel_payment", payment_id=payment_id, reason=reason)
        result = {
            "id": payment_id,
            "status": "canceled",
            "provider": "mock",
            "raw": self._stub("cancel"),
        }
        self._post("cancel_payment", result)
        return result

    def _create_subscription(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._pre("create_subscription", idempotency_key=idempotency_key)
        result = {
            "subscription_id": f"mock_sub_{uuid4().hex[:6]}",
            "status": "active",
            "provider": "mock",
            "raw": self._stub("subscription"),
        }
        self._post("create_subscription", result)
        return result

    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        self._pre("cancel_subscription", subscription_id=subscription_id)
        result = {
            "subscription_id": subscription_id,
            "status": "canceled",
            "provider": "mock",
            "raw": self._stub("subscription_cancel"),
        }
        self._post("cancel_subscription", result)
        return result

    def _create_invoice(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre("create_invoice")
        result = {
            "invoice_id": f"mock_inv_{uuid4().hex[:6]}",
            "status": "draft",
            "provider": "mock",
            "raw": self._stub("invoice"),
        }
        self._post("create_invoice", result)
        return result

    def _finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        self._pre("finalize_invoice", invoice_id=invoice_id)
        result = {
            "invoice_id": invoice_id,
            "status": "finalized",
            "provider": "mock",
            "raw": self._stub("invoice_finalize"),
        }
        self._post("finalize_invoice", result)
        return result

    def _void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        self._pre("void_invoice", invoice_id=invoice_id)
        result = {
            "invoice_id": invoice_id,
            "status": "void",
            "provider": "mock",
            "raw": self._stub("invoice_void"),
        }
        self._post("void_invoice", result)
        return result

    def _mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        self._pre("mark_uncollectible", invoice_id=invoice_id)
        result = {
            "invoice_id": invoice_id,
            "status": "uncollectible",
            "provider": "mock",
            "raw": self._stub("invoice_uncollectible"),
        }
        self._post("mark_uncollectible", result)
        return result

    def _create_split(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre("create_split", idempotency_key=idempotency_key)
        result = {"split": self._stub("split"), "provider": "mock"}
        self._post("create_split", result)
        return result

    def _charge_with_split(
        self,
        amount_minor: int,
        currency: str,
        *,
        split_code_or_params: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        self._pre("charge_with_split", amount_minor=amount_minor, currency=currency)
        result = {
            "payment_id": f"mock_pay_{uuid4().hex[:6]}",
            "status": "processing",
            "provider": "mock",
            "raw": self._stub("charge_split"),
        }
        self._post("charge_with_split", result)
        return result

    def _verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        self._pre("verify_webhook_signature", has_headers=bool(headers))
        self._post("verify_webhook_signature", True)
        return True

    def _list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        self._pre("list_disputes", limit=limit)
        disputes = [{"id": "mock_dispute_1", "provider": "mock", "status": "won"}]
        self._post("list_disputes", disputes)
        return disputes

    def _create_refund(
        self, payment: Any, req: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._pre("create_refund", payment=getattr(payment, "id", None))
        result = self._stub("refund_create")
        self._post("create_refund", result)
        return result

    def _get_refund(self, refund_id: str) -> Mapping[str, Any]:
        self._pre("get_refund", refund_id=refund_id)
        result = self._stub("refund_get", refund_id=refund_id)
        self._post("get_refund", result)
        return result

    def _create_customer(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre("create_customer")
        result = {
            "id": f"mock_cus_{uuid4().hex[:6]}",
            "provider": "mock",
            "raw": self._stub("customer"),
        }
        self._post("create_customer", result)
        return result

    def _get_customer(self, customer_id: str) -> Mapping[str, Any]:
        self._pre("get_customer", customer_id=customer_id)
        result = {
            "id": customer_id,
            "provider": "mock",
            "raw": self._stub("customer_get"),
        }
        self._post("get_customer", result)
        return result

    def _attach_payment_method_to_customer(
        self, customer: Any, pm: Any
    ) -> Mapping[str, Any]:
        self._pre("attach_payment_method_to_customer")
        result = self._stub("customer_attach_pm")
        self._post("attach_payment_method_to_customer", result)
        return result

    def _create_payment_method(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._pre("create_payment_method")
        result = {
            "id": f"mock_pm_{uuid4().hex[:6]}",
            "provider": "mock",
            "raw": self._stub("payment_method"),
        }
        self._post("create_payment_method", result)
        return result

    def _detach_payment_method(self, payment_method_id: str) -> Mapping[str, Any]:
        self._pre("detach_payment_method", payment_method_id=payment_method_id)
        result = self._stub("payment_method_detach")
        self._post("detach_payment_method", result)
        return result

    def _list_payment_methods(
        self,
        customer: Any,
        *,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> Sequence[Mapping[str, Any]]:
        self._pre("list_payment_methods", limit=limit)
        methods = [
            {
                "id": "mock_pm_1",
                "provider": "mock",
                "raw": self._stub("payment_method"),
            }
        ]
        self._post("list_payment_methods", methods)
        return methods

    def _create_payout(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre("create_payout", idempotency_key=idempotency_key)
        result = self._stub("payout", idempotency_key=idempotency_key)
        self._post("create_payout", result)
        return result

    def _get_balance(self) -> Mapping[str, Any]:
        self._pre("get_balance")
        result = {
            "snapshot_id": f"mock_bal_{uuid4().hex[:6]}",
            "provider": "mock",
            "raw": self._stub("balance"),
        }
        self._post("get_balance", result)
        return result

    def _create_transfer(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre("create_transfer", idempotency_key=idempotency_key)
        result = self._stub("transfer", idempotency_key=idempotency_key)
        self._post("create_transfer", result)
        return result

    def _create_report(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre("create_report", idempotency_key=idempotency_key)
        result = self._stub("report", idempotency_key=idempotency_key)
        self._post("create_report", result)
        return result

    def _parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> Mapping[str, Any]:
        self._pre("parse_event")
        result = {
            "event_id": "mock_evt_1",
            "provider": "mock",
            "type": "test.event",
            "raw": self._stub("event"),
        }
        self._post("parse_event", result)
        return result

    def _create_coupon(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre("create_coupon", idempotency_key=idempotency_key)
        result = self._stub("coupon", idempotency_key=idempotency_key)
        self._post("create_coupon", result)
        return result

    def _create_promotion(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._pre("create_promotion", idempotency_key=idempotency_key)
        result = self._stub("promotion", idempotency_key=idempotency_key)
        self._post("create_promotion", result)
        return result


__all__ = ["MockBillingProvider"]
