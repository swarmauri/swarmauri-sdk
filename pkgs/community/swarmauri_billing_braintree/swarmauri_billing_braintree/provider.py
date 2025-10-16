"""Braintree billing provider stub to mirror Swarmauri interfaces."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, cast
from uuid import uuid4

from swarmauri_base.billing import (
    BillingProviderBase,
    CustomersMixin,
    HostedCheckoutMixin,
    OnlinePaymentsMixin,
    PaymentMethodsMixin,
    ProductsPricesMixin,
    RefundsMixin,
    ReportsMixin,
    RiskMixin,
    SubscriptionsMixin,
    WebhooksMixin,
)
from swarmauri_core.billing import Capability


class BraintreeBillingProvider(
    ProductsPricesMixin,
    HostedCheckoutMixin,
    OnlinePaymentsMixin,
    SubscriptionsMixin,
    RefundsMixin,
    CustomersMixin,
    PaymentMethodsMixin,
    ReportsMixin,
    RiskMixin,
    WebhooksMixin,
    BillingProviderBase,
):
    """Stubbed Braintree provider featuring the primary Swarmauri capabilities."""

    CAPABILITIES = frozenset(
        {
            Capability.PRODUCTS_PRICES,
            Capability.HOSTED_CHECKOUT,
            Capability.ONLINE_PAYMENTS,
            Capability.SUBSCRIPTIONS,
            Capability.REFUNDS,
            Capability.CUSTOMERS,
            Capability.PAYMENT_METHODS,
            Capability.REPORTS,
            Capability.RISK,
            Capability.WEBHOOKS,
        }
    )
    component_name: str = "braintree"

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
            "id": f"bt_plan_{uuid4().hex[:8]}",
            "name": product_spec.resolve("name", "Braintree Plan"),
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
            "id": f"bt_price_{uuid4().hex[:8]}",
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
        return {
            "id": f"bt_checkout_{uuid4().hex[:8]}",
            "url": f"https://checkout.braintree.test/{uuid4().hex[:6]}",
            "provider": self.component_name,
            "raw": self._stub(
                "create_checkout",
                price_id=getattr(price, "id", ""),
                request=self._dump(request),
            ),
        }

    # ----------------------------------------------------------- online payments
    def _create_payment_intent(self, req: Any) -> Mapping[str, Any]:
        amount = int(req.resolve("amount_minor") or 0)
        currency = (req.resolve("currency") or "USD").upper()
        return {
            "id": f"bt_txn_{uuid4().hex[:8]}",
            "status": "AUTHORIZED"
            if req.resolve("confirm")
            else "SUBMITTED_FOR_SETTLEMENT",
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
            "status": "SETTLED",
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
            "status": "VOIDED",
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
            "subscription_id": f"bt_sub_{uuid4().hex[:8]}",
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
        status = "CANCELED" if not at_period_end else "ACTIVE_UNTIL_PERIOD_END"
        return {
            "subscription_id": subscription_id,
            "status": status,
            "provider": self.component_name,
            "raw": self._stub(
                "cancel_subscription",
                subscription_id=subscription_id,
                at_period_end=at_period_end,
            ),
        }

    # --------------------------------------------------------------------- refund
    def _create_refund(
        self, payment: Any, req: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return {
            "id": f"bt_refund_{uuid4().hex[:8]}",
            "status": "SUBMITTED",
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
            "status": "SETTLED",
            "provider": self.component_name,
            "raw": self._stub("get_refund", refund_id=refund_id),
        }

    # ------------------------------------------------------------------- customer
    def _create_customer(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        return {
            "id": f"bt_customer_{uuid4().hex[:8]}",
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
            "id": f"bt_pm_{uuid4().hex[:8]}",
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
        card_type = type or "credit_card"
        methods = []
        for index in range(min(limit, 2)):
            methods.append(
                {
                    "id": f"bt_pm_{index}",
                    "provider": self.component_name,
                    "type": card_type,
                    "raw": self._stub(
                        "list_payment_methods",
                        customer_id=getattr(customer, "id", ""),
                        type=card_type,
                        limit=limit,
                    ),
                }
            )
        return methods

    # --------------------------------------------------------------------- reports
    def _create_report(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        return {
            "report_id": f"bt_report_{uuid4().hex[:8]}",
            "status": "QUEUED",
            "provider": self.component_name,
            "raw": self._stub(
                "create_report",
                idempotency_key=idempotency_key,
                request=self._dump(req),
            ),
        }

    # ------------------------------------------------------------------------ risk
    def _verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        signature = headers.get("BT-Signature", "")
        return bool(signature and secret)

    def _list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        disputes = []
        for index in range(min(limit, 1)):
            disputes.append(
                {
                    "id": f"bt_dispute_{index}",
                    "status": "OPEN",
                    "provider": self.component_name,
                    "raw": self._stub("list_disputes", index=index),
                }
            )
        return disputes

    # --------------------------------------------------------------------- webhooks
    def _parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> Mapping[str, Any]:
        event_id = headers.get("BT-Webhook-Id") or f"bt_evt_{uuid4().hex[:8]}"
        return {
            "event_id": event_id,
            "type": headers.get("BT-Webhook-Kind", "braintree.event"),
            "provider": self.component_name,
            "raw": self._stub(
                "parse_event",
                headers=dict(headers),
                raw_body=raw_body.decode("utf-8", errors="ignore"),
            ),
        }


__all__ = ["BraintreeBillingProvider"]
