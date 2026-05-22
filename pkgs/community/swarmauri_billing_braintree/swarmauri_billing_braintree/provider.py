"""Braintree billing provider for Swarmauri interfaces."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, cast
from uuid import uuid4

from pydantic import Field, PrivateAttr, SecretStr

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
    """Braintree SDK backed provider featuring the primary Swarmauri capabilities."""

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
    merchant_id: str | None = Field(default=None, description="Braintree merchant ID")
    public_key: str | None = Field(default=None, description="Braintree public key")
    private_key: SecretStr | None = Field(
        default=None, description="Braintree private key"
    )
    environment: str = Field(default="sandbox", description="Braintree environment")
    _gateway: Any = PrivateAttr(default=None)

    def _bt(self) -> Any:
        if self._gateway is None:
            import braintree

            if not (self.merchant_id and self.public_key and self.private_key):
                raise ValueError(
                    "merchant_id, public_key, and private_key are required for Braintree API calls"
                )
            env = (
                braintree.Environment.Production
                if self.environment.lower() == "production"
                else braintree.Environment.Sandbox
            )
            self._gateway = braintree.BraintreeGateway(
                braintree.Configuration(
                    env,
                    merchant_id=self.merchant_id,
                    public_key=self.public_key,
                    private_key=self.private_key.get_secret_value(),
                )
            )
        return self._gateway

    @staticmethod
    def _result_payload(result: Any) -> Mapping[str, Any]:
        if not getattr(result, "is_success", False):
            raise RuntimeError(str(getattr(result, "message", result)))
        obj = getattr(result, "transaction", None)
        obj = obj or getattr(result, "customer", None)
        obj = obj or getattr(result, "payment_method", None)
        obj = obj or getattr(result, "subscription", None)
        obj = obj or getattr(result, "refund", None)
        if obj is None:
            return {"raw": str(result)}
        if hasattr(obj, "__dict__"):
            return dict(obj.__dict__)
        return {"raw": str(obj)}

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
        gateway = self._bt()
        amount = int(req.resolve("amount_minor") or 0)
        currency = (req.resolve("currency") or "USD").upper()
        metadata = dict(req.resolve("metadata") or {})
        sale = gateway.transaction.sale(
            {
                "amount": f"{amount / 100:.2f}",
                "payment_method_nonce": req.resolve("payment_method_id")
                or metadata.get("payment_method_nonce", "fake-valid-nonce"),
                "options": {"submit_for_settlement": bool(req.resolve("capture"))},
                "order_id": req.resolve("idempotency_key"),
            }
        )
        raw = self._result_payload(sale)
        return {
            "id": raw.get("id", f"bt_txn_{uuid4().hex[:8]}"),
            "status": raw.get("status"),
            "amount_minor": amount,
            "currency": currency,
            "provider": self.component_name,
            "raw": raw,
        }

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> Mapping[str, Any]:
        result = self._bt().transaction.submit_for_settlement(payment_id)
        raw = self._result_payload(result)
        return {
            "id": raw.get("id", payment_id),
            "status": raw.get("status"),
            "provider": self.component_name,
            "raw": raw,
        }

    def _cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Mapping[str, Any]:
        result = self._bt().transaction.void(payment_id)
        raw = self._result_payload(result)
        return {
            "id": raw.get("id", payment_id),
            "status": raw.get("status"),
            "provider": self.component_name,
            "raw": raw,
        }

    # --------------------------------------------------------------- subscription
    def _create_subscription(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        if not spec.items:
            raise ValueError("Braintree subscription creation requires a plan_id")
        result = self._bt().subscription.create(
            {
                "payment_method_token": (spec.metadata or {}).get(
                    "payment_method_token"
                ),
                "plan_id": spec.items[0].price_id,
            }
        )
        raw = self._result_payload(result)
        return {
            "subscription_id": raw.get("id", f"bt_sub_{uuid4().hex[:8]}"),
            "status": raw.get("status"),
            "provider": self.component_name,
            "raw": raw,
        }

    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        result = self._bt().subscription.cancel(subscription_id)
        raw = self._result_payload(result)
        return {
            "subscription_id": subscription_id,
            "status": raw.get("status", "Canceled"),
            "provider": self.component_name,
            "raw": raw,
        }

    # --------------------------------------------------------------------- refund
    def _create_refund(
        self, payment: Any, req: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        amount = req.resolve("amount_minor")
        result = self._bt().transaction.refund(
            getattr(payment, "id", ""),
            f"{int(amount) / 100:.2f}" if amount is not None else None,
        )
        raw = self._result_payload(result)
        return {
            "id": raw.get("id", f"bt_refund_{uuid4().hex[:8]}"),
            "status": raw.get("status"),
            "provider": self.component_name,
            "raw": raw,
        }

    def _get_refund(self, refund_id: str) -> Mapping[str, Any]:
        transaction = self._bt().transaction.find(refund_id)
        raw = dict(transaction.__dict__) if hasattr(transaction, "__dict__") else {}
        return {
            "id": refund_id,
            "status": raw.get("status"),
            "provider": self.component_name,
            "raw": raw,
        }

    # ------------------------------------------------------------------- customer
    def _create_customer(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        result = self._bt().customer.create(
            {
                "id": idempotency_key,
                "email": spec.resolve("email"),
                "first_name": spec.resolve("first_name"),
                "last_name": spec.resolve("last_name"),
            }
        )
        raw = self._result_payload(result)
        return {
            "id": raw.get("id", f"bt_customer_{uuid4().hex[:8]}"),
            "provider": self.component_name,
            "raw": raw,
        }

    def _get_customer(self, customer_id: str) -> Mapping[str, Any]:
        customer = self._bt().customer.find(customer_id)
        raw = dict(customer.__dict__) if hasattr(customer, "__dict__") else {}
        return {
            "id": customer_id,
            "provider": self.component_name,
            "raw": raw,
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
        result = self._bt().payment_method.create(
            {
                "customer_id": spec.resolve("customer_id"),
                "payment_method_nonce": spec.resolve("payment_method_nonce")
                or spec.resolve("nonce"),
                "token": idempotency_key,
            }
        )
        raw = self._result_payload(result)
        return {
            "id": raw.get("token", f"bt_pm_{uuid4().hex[:8]}"),
            "provider": self.component_name,
            "raw": raw,
        }

    def _detach_payment_method(self, payment_method_id: str) -> Mapping[str, Any]:
        self._bt().payment_method.delete(payment_method_id)
        return {"id": payment_method_id, "provider": self.component_name}

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
        payload = headers.get("BT-Payload") or raw_body.decode("utf-8")
        try:
            self._bt().webhook_notification.parse(signature, payload)
            return True
        except Exception:
            return False

    def _list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        # Braintree's Python SDK exposes disputes through a search iterator.
        rows = []
        for index, dispute in enumerate(self._bt().dispute.search()):
            if index >= limit:
                break
            rows.append(dict(dispute.__dict__) if hasattr(dispute, "__dict__") else {})
        return rows

    # --------------------------------------------------------------------- webhooks
    def _parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> Mapping[str, Any]:
        signature = headers.get("BT-Signature", "")
        payload = headers.get("BT-Payload") or raw_body.decode("utf-8")
        notification = self._bt().webhook_notification.parse(signature, payload)
        return {
            "event_id": getattr(notification, "timestamp", f"bt_evt_{uuid4().hex[:8]}"),
            "type": getattr(notification, "kind", "braintree.event"),
            "provider": self.component_name,
            "raw": dict(notification.__dict__),
        }


__all__ = ["BraintreeBillingProvider"]
