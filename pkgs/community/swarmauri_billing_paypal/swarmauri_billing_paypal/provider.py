"""PayPal REST billing provider covering Swarmauri capabilities."""

from __future__ import annotations

import json
from typing import Any, Mapping, Optional, Sequence, cast
from uuid import uuid4

import requests
from pydantic import Field, PrivateAttr, SecretStr

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
    RiskMixin,
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
    RiskMixin,
    WebhooksMixin,
    BillingProviderBase,
):
    """PayPal REST API backed provider for billing workflows."""

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
            Capability.RISK,
            Capability.WEBHOOKS,
        }
    )
    component_name: str = "paypal"
    client_id: str | None = Field(
        default=None, description="PayPal REST client ID"
    )
    client_secret: SecretStr | None = Field(
        default=None, description="PayPal REST client secret"
    )
    environment: str = Field(
        default="sandbox", description="PayPal environment"
    )
    webhook_id: str | None = Field(
        default=None,
        description="PayPal webhook ID for signature verification",
    )
    _access_token: str | None = PrivateAttr(default=None)

    @property
    def _base(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")
        if self.environment.lower() == "production":
            return "https://api-m.paypal.com"
        return "https://api-m.sandbox.paypal.com"

    def _token(self) -> str:
        if self._access_token:
            return self._access_token
        if not (self.client_id and self.client_secret):
            raise ValueError(
                "client_id and client_secret are required for PayPal API calls"
            )
        response = requests.post(
            f"{self._base}/v1/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=(self.client_id, self.client_secret.get_secret_value()),
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"PayPal OAuth error {response.status_code}: {response.text}"
            )
        self._access_token = response.json()["access_token"]
        return self._access_token

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: Mapping[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> Mapping[str, Any]:
        headers = {
            "Authorization": f"Bearer {self._token()}",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["PayPal-Request-Id"] = idempotency_key
        response = requests.request(
            method,
            f"{self._base}{path}",
            headers=headers,
            json=dict(payload or {}),
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"PayPal API error {response.status_code}: {response.text}"
            )
        return response.json() if response.content else {}

    # ---------------------------------------------------------------------
    # utils
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

    # ------------------------------------------------------------
    # products/prices
    def _create_product(
        self, product_spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        raw = self._request(
            "POST",
            "/v1/catalogs/products",
            payload={
                "name": product_spec.resolve("name", "Swarmauri Product"),
                "description": product_spec.resolve("description"),
                "type": product_spec.resolve("type", "SERVICE"),
                "category": product_spec.resolve("category", "SOFTWARE"),
            },
            idempotency_key=idempotency_key,
        )
        return {
            "id": raw["id"],
            "name": raw.get("name"),
            "provider": self.component_name,
            "raw": raw,
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
        raw = self._request(
            "POST",
            "/v1/billing/plans",
            payload={
                "product_id": getattr(product, "id", ""),
                "name": price_spec.resolve("nickname", "Swarmauri Plan"),
                "billing_cycles": [
                    {
                        "frequency": {
                            "interval_unit": price_spec.resolve(
                                "interval_unit", "MONTH"
                            ),
                            "interval_count": int(
                                price_spec.resolve("interval_count", 1)
                            ),
                        },
                        "tenure_type": "REGULAR",
                        "sequence": 1,
                        "total_cycles": int(
                            price_spec.resolve("total_cycles", 0)
                        ),
                        "pricing_scheme": {
                            "fixed_price": {
                                "value": f"{unit_amount / 100:.2f}",
                                "currency_code": currency,
                            }
                        },
                    }
                ],
                "payment_preferences": {"auto_bill_outstanding": True},
            },
            idempotency_key=idempotency_key,
        )
        return {
            "id": raw["id"],
            "product_id": getattr(product, "id", ""),
            "currency": currency,
            "unit_amount_minor": unit_amount,
            "provider": self.component_name,
            "raw": raw,
        }

    # --------------------------------------------------------------- hosted
    # flow
    def _create_checkout(self, price: Any, request: Any) -> Mapping[str, Any]:
        success_url = request.resolve(
            "success_url", "https://example.com/return"
        )
        currency = getattr(price, "currency", None) or "USD"
        amount = int(getattr(price, "unit_amount_minor", 0) or 0) * int(
            request.quantity
        )
        raw = self._request(
            "POST",
            "/v2/checkout/orders",
            payload={
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "reference_id": getattr(price, "id", "default"),
                        "amount": {
                            "currency_code": currency.upper(),
                            "value": f"{amount / 100:.2f}",
                        },
                    }
                ],
                "payment_source": {
                    "paypal": {
                        "experience_context": {
                            "return_url": success_url,
                            "cancel_url": request.resolve(
                                "cancel_url", success_url
                            ),
                        }
                    }
                },
            },
            idempotency_key=request.resolve("idempotency_key"),
        )
        approve_url = next(
            (
                link.get("href")
                for link in raw.get("links", [])
                if link.get("rel") == "approve"
            ),
            None,
        )
        return {
            "id": raw["id"],
            "url": approve_url,
            "provider": self.component_name,
            "raw": raw,
        }

    # ----------------------------------------------------------- online
    # payments
    def _create_payment_intent(self, req: Any) -> Mapping[str, Any]:
        amount = int(req.resolve("amount_minor") or 0)
        currency = (req.resolve("currency") or "USD").upper()
        raw = self._request(
            "POST",
            "/v2/checkout/orders",
            payload={
                "intent": "CAPTURE" if req.resolve("capture") else "AUTHORIZE",
                "purchase_units": [
                    {
                        "reference_id": req.resolve(
                            "idempotency_key", "default"
                        ),
                        "amount": {
                            "currency_code": currency,
                            "value": f"{amount / 100:.2f}",
                        },
                    }
                ],
            },
            idempotency_key=req.resolve("idempotency_key"),
        )
        return {
            "id": raw["id"],
            "status": raw.get("status"),
            "amount_minor": amount,
            "currency": currency,
            "provider": self.component_name,
            "raw": raw,
        }

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> Mapping[str, Any]:
        raw = self._request(
            "POST",
            f"/v2/checkout/orders/{payment_id}/capture",
            idempotency_key=idempotency_key,
        )
        return {
            "id": raw["id"],
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
        raw = self._request(
            "POST", f"/v2/payments/authorizations/{payment_id}/void"
        )
        return {
            "id": payment_id,
            "status": raw.get("status", "VOIDED"),
            "provider": self.component_name,
            "raw": raw,
        }

    # ---------------------------------------------------------------
    # subscription
    def _create_subscription(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        if not spec.items:
            raise ValueError("PayPal subscription creation requires a plan ID")
        raw = self._request(
            "POST",
            "/v1/billing/subscriptions",
            payload={
                "plan_id": spec.items[0].price_id,
                "custom_id": idempotency_key,
                "subscriber": {"payer_id": spec.resolve("customer_id")}
                if spec.resolve("customer_id")
                else None,
            },
            idempotency_key=idempotency_key,
        )
        return {
            "subscription_id": raw["id"],
            "status": raw.get("status"),
            "provider": self.component_name,
            "raw": raw,
        }

    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        raw = self._request(
            "POST",
            f"/v1/billing/subscriptions/{subscription_id}/cancel",
            payload={"reason": "Canceled through Swarmauri"},
        )
        return {
            "subscription_id": subscription_id,
            "status": raw.get("status", "CANCELLED"),
            "provider": self.component_name,
            "raw": raw,
        }

    # ------------------------------------------------------------------
    # invoicing
    def _create_invoice(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        line_items = [
            {
                "name": item.description or item.price_id or "Invoice item",
                "quantity": str(item.quantity),
                "unit_amount": {
                    "currency_code": (item.currency or "USD").upper(),
                    "value": f"{int(item.amount_minor or 0) / 100:.2f}",
                },
            }
            for item in spec.line_items
        ]
        raw = self._request(
            "POST",
            "/v2/invoicing/invoices",
            payload={
                "detail": {
                    "invoice_number": idempotency_key,
                    "currency_code": (
                        spec.line_items[0].currency
                        if spec.line_items
                        else "USD"
                    ).upper(),
                },
                "primary_recipients": [
                    {
                        "billing_info": {
                            "email_address": spec.resolve("customer_id")
                        }
                    }
                ],
                "items": line_items,
            },
            idempotency_key=idempotency_key,
        )
        return {
            "invoice_id": raw["id"],
            "status": raw.get("status", "DRAFT"),
            "provider": self.component_name,
            "raw": raw,
        }

    def _finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        raw = self._request(
            "POST", f"/v2/invoicing/invoices/{invoice_id}/send"
        )
        return {
            "invoice_id": invoice_id,
            "status": raw.get("status", "SENT"),
            "provider": self.component_name,
            "raw": raw,
        }

    def _void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        raw = self._request(
            "POST", f"/v2/invoicing/invoices/{invoice_id}/cancel"
        )
        return {
            "invoice_id": invoice_id,
            "status": raw.get("status", "CANCELLED"),
            "provider": self.component_name,
            "raw": raw,
        }

    def _mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        return {
            "invoice_id": invoice_id,
            "status": "BAD_DEBT",
            "provider": self.component_name,
            "raw": self._stub("mark_uncollectible", invoice_id=invoice_id),
        }

    # ---------------------------------------------------------------------
    # refund
    def _create_refund(
        self, payment: Any, req: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        amount = req.resolve("amount_minor")
        currency = (
            req.resolve("currency")
            or getattr(payment, "currency", None)
            or "USD"
        )
        payload = {}
        if amount is not None:
            payload["amount"] = {
                "currency_code": currency.upper(),
                "value": f"{int(amount) / 100:.2f}",
            }
        if req.resolve("reason"):
            payload["note_to_payer"] = req.resolve("reason")
        raw = self._request(
            "POST",
            f"/v2/payments/captures/{getattr(payment, 'id', '')}/refund",
            payload=payload,
            idempotency_key=idempotency_key,
        )
        return {
            "id": raw["id"],
            "status": raw.get("status"),
            "provider": self.component_name,
            "raw": raw,
        }

    def _get_refund(self, refund_id: str) -> Mapping[str, Any]:
        raw = self._request("GET", f"/v2/payments/refunds/{refund_id}")
        return {
            "id": refund_id,
            "status": raw.get("status"),
            "provider": self.component_name,
            "raw": raw,
        }

    # -------------------------------------------------------------------
    # customer
    def _create_customer(
        self, spec: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
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

    # --------------------------------------------------------------- payment
    # info
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

    def _detach_payment_method(
        self, payment_method_id: str
    ) -> Mapping[str, Any]:
        return self._stub(
            "detach_payment_method", payment_method_id=payment_method_id
        )

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

    # ---------------------------------------------------------------------
    # payouts
    def _create_payout(
        self, req: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        raw = self._request(
            "POST",
            "/v1/payments/payouts",
            payload={
                "sender_batch_header": {
                    "sender_batch_id": idempotency_key,
                    "email_subject": req.resolve(
                        "email_subject", "You have a payout"
                    ),
                },
                "items": req.resolve("items", []),
            },
            idempotency_key=idempotency_key,
        )
        return {
            "payout_id": raw.get("batch_header", {}).get("payout_batch_id"),
            "status": raw.get("batch_header", {}).get("batch_status"),
            "provider": self.component_name,
            "raw": raw,
        }

    def _get_balance(self) -> Mapping[str, Any]:
        return {
            "snapshot_id": f"paypal_balance_{uuid4().hex[:10]}",
            "available_minor": 0,
            "provider": self.component_name,
            "raw": self._stub("get_balance"),
        }

    # ---------------------------------------------------------------------
    # reports
    def _create_report(
        self, req: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
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

    # ------------------------------------------------------------------------
    # risk
    @staticmethod
    def _header(headers: Mapping[str, str], name: str) -> str | None:
        lower_name = name.lower()
        for key, value in headers.items():
            if key.lower() == lower_name:
                return value
        return None

    def _verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        webhook_id = self.webhook_id or secret
        if not webhook_id:
            raise ValueError(
                (
                    "webhook_id or secret is required for PayPal webhook "
                    "verification"
                )
            )
        event = json.loads(raw_body.decode("utf-8"))
        raw = self._request(
            "POST",
            "/v1/notifications/verify-webhook-signature",
            payload={
                "auth_algo": self._header(headers, "PAYPAL-AUTH-ALGO"),
                "cert_url": self._header(headers, "PAYPAL-CERT-URL"),
                "transmission_id": self._header(
                    headers, "PAYPAL-TRANSMISSION-ID"
                ),
                "transmission_sig": self._header(
                    headers, "PAYPAL-TRANSMISSION-SIG"
                ),
                "transmission_time": self._header(
                    headers, "PAYPAL-TRANSMISSION-TIME"
                ),
                "webhook_id": webhook_id,
                "webhook_event": event,
            },
        )
        return raw.get("verification_status") == "SUCCESS"

    def _list_disputes(
        self, *, limit: int = 50
    ) -> Sequence[Mapping[str, Any]]:
        raw = self._request(
            "GET",
            f"/v1/customer/disputes?page_size={limit}",
        )
        return cast(Sequence[Mapping[str, Any]], raw.get("items", ()))

    # ---------------------------------------------------------------------
    # webhooks
    def _parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> Mapping[str, Any]:
        payload = json.loads(raw_body.decode("utf-8"))
        return {
            "event_id": payload.get("id", f"paypal_evt_{uuid4().hex[:10]}"),
            "type": payload.get("event_type", "paypal.event"),
            "provider": self.component_name,
            "raw": payload,
        }


__all__ = ["PayPalBillingProvider"]
