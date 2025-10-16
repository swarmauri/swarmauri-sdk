"""PayPal billing provider stub covering Swarmauri capabilities."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, cast
from uuid import uuid4

from swarmauri_base.billing import (
    BillingProviderBase,
    CustomersMixin,
    HostedCheckoutMixin,
    InvoicingMixin,
    OnlinePaymentsMixin,
    PaymentMethodsMixin,
    PayoutsMixin,
    ProductsPricesMixin,
    RefundsMixin,
    ReportsMixin,
    SubscriptionsMixin,
    WebhooksMixin,
)
from swarmauri_core.billing import Capability


class PayPalBillingProvider(
    ProductsPricesMixin,
    HostedCheckoutMixin,
    OnlinePaymentsMixin,
    SubscriptionsMixin,
    InvoicingMixin,
    RefundsMixin,
    CustomersMixin,
    PaymentMethodsMixin,
    PayoutsMixin,
    ReportsMixin,
    WebhooksMixin,
    BillingProviderBase,
):
    """Deterministic PayPal-like provider for local development and tests."""

    CAPABILITIES = frozenset(
        {
            Capability.PRODUCTS_PRICES,
            Capability.HOSTED_CHECKOUT,
            Capability.ONLINE_PAYMENTS,
            Capability.SUBSCRIPTIONS,
            Capability.INVOICING,
            Capability.REFUNDS,
            Capability.CUSTOMERS,
            Capability.PAYMENT_METHODS,
            Capability.PAYOUTS,
            Capability.REPORTS,
            Capability.WEBHOOKS,
        }
    )
    component_name: str = "paypal"

    # --------------------------------------------------------------------- utils
    @staticmethod
    def _dump(obj: Any) -> Mapping[str, Any]:
        if hasattr(obj, "model_dump"):
            return cast(Mapping[str, Any], obj.model_dump(exclude_none=True))
        if hasattr(obj, "dict"):
            return cast(Mapping[str, Any], obj.dict(exclude_none=True))
        if isinstance(obj, Mapping):
            return obj
        return {}

    def _stub(self, action: str, **payload: Any) -> Mapping[str, Any]:
        return {
            "provider": self.component_name,
            "action": action,
            "payload": payload,
        }

    # ------------------------------------------------------------ products/prices
    def _create_product(
        self, product_spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return {
            "id": f"paypal_prod_{uuid4().hex[:10]}",
            "name": product_spec.resolve("name", "PayPal Product"),
            "provider": self.component_name,
            "raw": self._stub(
                "create_product",
                idempotency_key=idempotency_key,
                product=self._dump(product_spec),
            ),
        }

    def _create_price(
        self,
        product: Any,
        price_spec: Any,
        *,
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        currency = (price_spec.resolve("currency") or "USD").upper()
        unit_amount = int(price_spec.resolve("unit_amount_minor") or 0)
        return {
            "id": f"paypal_price_{uuid4().hex[:10]}",
            "product_id": getattr(product, "id", ""),
            "currency": currency,
            "unit_amount_minor": unit_amount,
            "provider": self.component_name,
            "raw": self._stub(
                "create_price",
                idempotency_key=idempotency_key,
                price=self._dump(price_spec),
            ),
        }

    # --------------------------------------------------------------- hosted flow
    def _create_checkout(self, price: Any, request: Any) -> Mapping[str, Any]:
        success_url = request.resolve("success_url", "https://example.com/return")
        return {
            "id": f"paypal_checkout_{uuid4().hex[:10]}",
            "url": f"https://paypal.example/checkout/{uuid4().hex[:8]}",
            "provider": self.component_name,
            "raw": self._stub(
                "create_checkout",
                price_id=getattr(price, "id", ""),
                success_url=success_url,
                request=self._dump(request),
            ),
        }

    # ----------------------------------------------------------- online payments
    def _create_payment_intent(self, req: Any) -> Mapping[str, Any]:
        amount = int(req.resolve("amount_minor") or 0)
        currency = (req.resolve("currency") or "USD").upper()
        return {
            "id": f"paypal_pay_{uuid4().hex[:10]}",
            "status": "APPROVED" if req.resolve("confirm") else "CREATED",
            "amount_minor": amount,
            "currency": currency,
            "provider": self.component_name,
            "raw": self._stub("create_payment_intent", request=self._dump(req)),
        }

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> Mapping[str, Any]:
        return {
            "id": payment_id,
            "status": "COMPLETED",
            "provider": self.component_name,
            "raw": self._stub(
                "capture_payment",
                payment_id=payment_id,
                idempotency_key=idempotency_key,
            ),
        }

    def _cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Mapping[str, Any]:
        return {
            "id": payment_id,
            "status": "CANCELED",
            "provider": self.component_name,
            "raw": self._stub(
                "cancel_payment",
                payment_id=payment_id,
                reason=reason,
                idempotency_key=idempotency_key,
            ),
        }

    # --------------------------------------------------------------- subscription
    def _create_subscription(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return {
            "subscription_id": f"paypal_sub_{uuid4().hex[:10]}",
            "status": "ACTIVE",
            "provider": self.component_name,
            "raw": self._stub(
                "create_subscription",
                idempotency_key=idempotency_key,
                spec=self._dump(spec),
            ),
        }

    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        return {
            "subscription_id": subscription_id,
            "status": "CANCELLED" if not at_period_end else "ACTIVE_UNTIL_PERIOD_END",
            "provider": self.component_name,
            "raw": self._stub(
                "cancel_subscription",
                subscription_id=subscription_id,
                at_period_end=at_period_end,
            ),
        }

    # ------------------------------------------------------------------ invoicing
    def _create_invoice(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        return {
            "invoice_id": f"paypal_inv_{uuid4().hex[:10]}",
            "status": "DRAFT",
            "provider": self.component_name,
            "raw": self._stub(
                "create_invoice",
                idempotency_key=idempotency_key,
                spec=self._dump(spec),
            ),
        }

    def _finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        return {
            "invoice_id": invoice_id,
            "status": "SENT",
            "provider": self.component_name,
            "raw": self._stub("finalize_invoice", invoice_id=invoice_id),
        }

    def _void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        return {
            "invoice_id": invoice_id,
            "status": "VOIDED",
            "provider": self.component_name,
            "raw": self._stub("void_invoice", invoice_id=invoice_id),
        }

    def _mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        return {
            "invoice_id": invoice_id,
            "status": "BAD_DEBT",
            "provider": self.component_name,
            "raw": self._stub("mark_uncollectible", invoice_id=invoice_id),
        }

    # --------------------------------------------------------------------- refund
    def _create_refund(
        self, payment: Any, req: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return {
            "id": f"paypal_refund_{uuid4().hex[:8]}",
            "status": "PENDING",
            "provider": self.component_name,
            "raw": self._stub(
                "create_refund",
                payment_id=getattr(payment, "id", ""),
                request=self._dump(req),
                idempotency_key=idempotency_key,
            ),
        }

    def _get_refund(self, refund_id: str) -> Mapping[str, Any]:
        return {
            "id": refund_id,
            "status": "COMPLETED",
            "provider": self.component_name,
            "raw": self._stub("get_refund", refund_id=refund_id),
        }

    # ------------------------------------------------------------------- customer
    def _create_customer(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        return {
            "id": f"paypal_cus_{uuid4().hex[:10]}",
            "provider": self.component_name,
            "raw": self._stub(
                "create_customer",
                idempotency_key=idempotency_key,
                spec=self._dump(spec),
            ),
        }

    def _get_customer(self, customer_id: str) -> Mapping[str, Any]:
        return {
            "id": customer_id,
            "provider": self.component_name,
            "raw": self._stub("get_customer", customer_id=customer_id),
        }

    def _attach_payment_method_to_customer(
        self, customer: Any, pm: Any
    ) -> Mapping[str, Any]:
        return self._stub(
            "attach_payment_method",
            customer_id=getattr(customer, "id", ""),
            payment_method_id=getattr(pm, "id", ""),
        )

    # --------------------------------------------------------------- payment info
    def _create_payment_method(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return {
            "id": f"paypal_pm_{uuid4().hex[:10]}",
            "provider": self.component_name,
            "raw": self._stub(
                "create_payment_method",
                idempotency_key=idempotency_key,
                spec=self._dump(spec),
            ),
        }

    def _detach_payment_method(self, payment_method_id: str) -> Mapping[str, Any]:
        return self._stub("detach_payment_method", payment_method_id=payment_method_id)

    def _list_payment_methods(
        self,
        customer: Any,
        *,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> Sequence[Mapping[str, Any]]:
        items = []
        for index in range(min(limit, 3)):
            items.append(
                {
                    "id": f"paypal_pm_{index}",
                    "provider": self.component_name,
                    "type": type or "CARD",
                    "raw": self._stub(
                        "list_payment_methods",
                        customer_id=getattr(customer, "id", ""),
                        type=type,
                        limit=limit,
                    ),
                }
            )
        return items

    # --------------------------------------------------------------------- payouts
    def _create_payout(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        return {
            "payout_id": f"paypal_payout_{uuid4().hex[:10]}",
            "status": "PROCESSING",
            "provider": self.component_name,
            "raw": self._stub(
                "create_payout",
                idempotency_key=idempotency_key,
                request=self._dump(req),
            ),
        }

    def _get_balance(self) -> Mapping[str, Any]:
        return {
            "snapshot_id": f"paypal_balance_{uuid4().hex[:10]}",
            "available_minor": 0,
            "provider": self.component_name,
            "raw": self._stub("get_balance"),
        }

    # --------------------------------------------------------------------- reports
    def _create_report(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        return {
            "report_id": f"paypal_report_{uuid4().hex[:10]}",
            "status": "QUEUED",
            "provider": self.component_name,
            "raw": self._stub(
                "create_report",
                idempotency_key=idempotency_key,
                request=self._dump(req),
            ),
        }

    # --------------------------------------------------------------------- webhooks
    def _parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> Mapping[str, Any]:
        return {
            "event_id": f"paypal_evt_{uuid4().hex[:10]}",
            "type": headers.get("PayPal-Transmission-Id", "paypal.event"),
            "provider": self.component_name,
            "raw": self._stub(
                "parse_event",
                headers=dict(headers),
                raw_body=raw_body.decode("utf-8", errors="ignore"),
            ),
        }


__all__ = ["PayPalBillingProvider"]
