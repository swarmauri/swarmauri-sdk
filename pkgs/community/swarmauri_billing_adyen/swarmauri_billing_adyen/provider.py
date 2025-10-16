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
        self._pre(
            "create_product",
            idempotency_key=idempotency_key,
            spec=getattr(product_spec, "model_dump", lambda **_: product_spec)(),
        )
        result = {
            "id": f"ady_prod_{uuid4().hex[:8]}",
            "provider": "adyen",
            "name": getattr(product_spec, "name", "Adyen Product"),
            "raw": self._stub("product", idempotency_key=idempotency_key),
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
        self._pre(
            "create_price",
            product=getattr(product, "id", None),
            spec=getattr(price_spec, "model_dump", lambda **_: price_spec)(),
            idempotency_key=idempotency_key,
        )
        result = {
            "id": f"ady_price_{uuid4().hex[:8]}",
            "product_id": getattr(product, "id", ""),
            "provider": "adyen",
            "raw": self._stub("price", idempotency_key=idempotency_key),
        }
        self._post("create_price", result)
        return result

    # ---------------------------------------------------------------- Hosted Checkout
    def _create_checkout(self, price: Any, request: Any) -> Mapping[str, Any]:
        self._pre(
            "create_checkout",
            price=getattr(price, "id", None),
            request=getattr(request, "model_dump", lambda **_: request)(),
        )
        result = {
            "id": f"ady_chk_{uuid4().hex[:10]}",
            "url": "https://checkout.adyen.example/session",
            "provider": "adyen",
            "raw": self._stub("checkout"),
        }
        self._post("create_checkout", result)
        return result

    # ---------------------------------------------------------------- Online Payments
    def _create_payment_intent(self, req: Any) -> Mapping[str, Any]:
        self._pre(
            "create_payment_intent",
            request=getattr(req, "model_dump", lambda **_: req)(),
        )
        result = {
            "id": f"ady_pi_{uuid4().hex[:10]}",
            "status": "requires_action",
            "provider": "adyen",
            "raw": self._stub("payment_intent"),
        }
        self._post("create_payment_intent", result)
        return result

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> Mapping[str, Any]:
        self._pre(
            "capture_payment",
            payment_id=payment_id,
            idempotency_key=idempotency_key,
        )
        result = {
            "id": payment_id,
            "status": "succeeded",
            "provider": "adyen",
            "raw": self._stub("capture", payment_id=payment_id),
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
        self._pre(
            "cancel_payment",
            payment_id=payment_id,
            reason=reason,
            idempotency_key=idempotency_key,
        )
        result = {
            "id": payment_id,
            "status": "canceled",
            "provider": "adyen",
            "raw": self._stub("cancel", payment_id=payment_id, reason=reason),
        }
        self._post("cancel_payment", result)
        return result

    # ---------------------------------------------------------------- Subscriptions
    def _create_subscription(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._pre(
            "create_subscription",
            spec=getattr(spec, "model_dump", lambda **_: spec)(),
            idempotency_key=idempotency_key,
        )
        result = {
            "subscription_id": f"ady_sub_{uuid4().hex[:8]}",
            "status": "active",
            "provider": "adyen",
            "raw": self._stub("subscription_create"),
        }
        self._post("create_subscription", result)
        return result

    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        self._pre(
            "cancel_subscription",
            subscription_id=subscription_id,
            at_period_end=at_period_end,
        )
        result = {
            "subscription_id": subscription_id,
            "status": "canceled",
            "provider": "adyen",
            "raw": self._stub("subscription_cancel"),
        }
        self._post("cancel_subscription", result)
        return result

    # ---------------------------------------------------------------- Invoicing
    def _create_invoice(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre(
            "create_invoice",
            spec=getattr(spec, "model_dump", lambda **_: spec)(),
            idempotency_key=idempotency_key,
        )
        result = {
            "invoice_id": f"ady_inv_{uuid4().hex[:8]}",
            "status": "draft",
            "provider": "adyen",
            "raw": self._stub("invoice_create"),
        }
        self._post("create_invoice", result)
        return result

    def _finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        self._pre("finalize_invoice", invoice_id=invoice_id)
        result = {
            "invoice_id": invoice_id,
            "status": "finalized",
            "provider": "adyen",
            "raw": self._stub("invoice_finalize"),
        }
        self._post("finalize_invoice", result)
        return result

    def _void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        self._pre("void_invoice", invoice_id=invoice_id)
        result = {
            "invoice_id": invoice_id,
            "status": "void",
            "provider": "adyen",
            "raw": self._stub("invoice_void"),
        }
        self._post("void_invoice", result)
        return result

    def _mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        self._pre("mark_uncollectible", invoice_id=invoice_id)
        result = {
            "invoice_id": invoice_id,
            "status": "uncollectible",
            "provider": "adyen",
            "raw": self._stub("invoice_uncollectible"),
        }
        self._post("mark_uncollectible", result)
        return result

    # ---------------------------------------------------------------- Marketplace
    def _create_split(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre(
            "create_split",
            spec=getattr(spec, "model_dump", lambda **_: spec)(),
            idempotency_key=idempotency_key,
        )
        result = {
            "split": self._stub("split_create"),
            "provider": "adyen",
        }
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
        self._pre(
            "charge_with_split",
            amount_minor=amount_minor,
            currency=currency,
            split=split_code_or_params,
            idempotency_key=idempotency_key,
        )
        result = {
            "payment_id": f"ady_pay_{uuid4().hex[:10]}",
            "status": "processing",
            "provider": "adyen",
            "raw": self._stub("charge_split"),
        }
        self._post("charge_with_split", result)
        return result

    # ---------------------------------------------------------------- Risk
    def _verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        self._pre("verify_webhook_signature", has_headers=bool(headers))
        self._post("verify_webhook_signature", True)
        return True

    def _list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        self._pre("list_disputes", limit=limit)
        disputes = [
            {
                "id": f"ady_dispute_{uuid4().hex[:8]}",
                "provider": "adyen",
                "status": "in_progress",
            }
        ]
        self._post("list_disputes", disputes)
        return disputes

    # ---------------------------------------------------------------- Refunds
    def _create_refund(
        self, payment: Any, req: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._pre(
            "create_refund",
            payment=getattr(payment, "id", None),
            request=getattr(req, "model_dump", lambda **_: req)(),
            idempotency_key=idempotency_key,
        )
        result = self._stub("refund_create", idempotency_key=idempotency_key)
        self._post("create_refund", result)
        return result

    def _get_refund(self, refund_id: str) -> Mapping[str, Any]:
        self._pre("get_refund", refund_id=refund_id)
        result = self._stub("refund_get", refund_id=refund_id)
        self._post("get_refund", result)
        return result

    # ---------------------------------------------------------------- Customers
    def _create_customer(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre(
            "create_customer",
            spec=getattr(spec, "model_dump", lambda **_: spec)(),
            idempotency_key=idempotency_key,
        )
        result = {
            "id": f"ady_cus_{uuid4().hex[:8]}",
            "provider": "adyen",
            "raw": self._stub("customer_create"),
        }
        self._post("create_customer", result)
        return result

    def _get_customer(self, customer_id: str) -> Mapping[str, Any]:
        self._pre("get_customer", customer_id=customer_id)
        result = {
            "id": customer_id,
            "provider": "adyen",
            "raw": self._stub("customer_get"),
        }
        self._post("get_customer", result)
        return result

    def _attach_payment_method_to_customer(
        self, customer: Any, pm: Any
    ) -> Mapping[str, Any]:
        self._pre(
            "attach_payment_method_to_customer",
            customer=getattr(customer, "id", None),
            payment_method=getattr(pm, "id", None),
        )
        result = self._stub(
            "customer_attach_pm",
            customer_id=getattr(customer, "id", None),
            payment_method_id=getattr(pm, "id", None),
        )
        self._post("attach_payment_method_to_customer", result)
        return result

    # ---------------------------------------------------------------- Payment Methods
    def _create_payment_method(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._pre(
            "create_payment_method",
            spec=getattr(spec, "model_dump", lambda **_: spec)(),
            idempotency_key=idempotency_key,
        )
        result = {
            "id": f"ady_pm_{uuid4().hex[:8]}",
            "provider": "adyen",
            "raw": self._stub("payment_method_create"),
        }
        self._post("create_payment_method", result)
        return result

    def _detach_payment_method(self, payment_method_id: str) -> Mapping[str, Any]:
        self._pre("detach_payment_method", payment_method_id=payment_method_id)
        result = self._stub(
            "payment_method_detach", payment_method_id=payment_method_id
        )
        self._post("detach_payment_method", result)
        return result

    def _list_payment_methods(
        self,
        customer: Any,
        *,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> Sequence[Mapping[str, Any]]:
        self._pre(
            "list_payment_methods",
            customer=getattr(customer, "id", None),
            type=type,
            limit=limit,
        )
        methods = [
            {
                "id": f"ady_pm_{uuid4().hex[:8]}",
                "provider": "adyen",
                "raw": self._stub("payment_method"),
            }
        ]
        self._post("list_payment_methods", methods)
        return methods

    # ---------------------------------------------------------------- Payouts
    def _create_payout(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre(
            "create_payout",
            request=getattr(req, "model_dump", lambda **_: req)(),
            idempotency_key=idempotency_key,
        )
        result = self._stub("payout_create", idempotency_key=idempotency_key)
        self._post("create_payout", result)
        return result

    # ---------------------------------------------------------------- Balance & Transfers
    def _get_balance(self) -> Mapping[str, Any]:
        self._pre("get_balance")
        result = {
            "snapshot_id": f"ady_bal_{uuid4().hex[:6]}",
            "provider": "adyen",
            "raw": self._stub("balance"),
        }
        self._post("get_balance", result)
        return result

    def _create_transfer(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre(
            "create_transfer",
            request=getattr(req, "model_dump", lambda **_: req)(),
            idempotency_key=idempotency_key,
        )
        result = self._stub("transfer_create", idempotency_key=idempotency_key)
        self._post("create_transfer", result)
        return result

    # ---------------------------------------------------------------- Reports
    def _create_report(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre(
            "create_report",
            request=getattr(req, "model_dump", lambda **_: req)(),
            idempotency_key=idempotency_key,
        )
        result = self._stub("report_create", idempotency_key=idempotency_key)
        self._post("create_report", result)
        return result

    # ---------------------------------------------------------------- Webhooks
    def _parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> Mapping[str, Any]:
        self._pre("parse_event", has_headers=bool(headers))
        result = {
            "event_id": f"ady_evt_{uuid4().hex[:8]}",
            "provider": "adyen",
            "type": "AUTHORISATION",
            "raw": self._stub("event"),
        }
        self._post("parse_event", result)
        return result

    # ---------------------------------------------------------------- Promotions
    def _create_coupon(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        self._pre(
            "create_coupon",
            spec=getattr(spec, "model_dump", lambda **_: spec)(),
            idempotency_key=idempotency_key,
        )
        result = self._stub("coupon_create", idempotency_key=idempotency_key)
        self._post("create_coupon", result)
        return result

    def _create_promotion(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._pre(
            "create_promotion",
            spec=getattr(spec, "model_dump", lambda **_: spec)(),
            idempotency_key=idempotency_key,
        )
        result = self._stub("promotion_create", idempotency_key=idempotency_key)
        self._post("create_promotion", result)
        return result


__all__ = ["AdyenBillingProvider"]
