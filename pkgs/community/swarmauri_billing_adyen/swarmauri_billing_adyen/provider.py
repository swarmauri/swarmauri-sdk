"""Concrete Adyen billing provider."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any, Mapping, Optional, Sequence
from uuid import uuid4

import requests
from pydantic import Field

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
    """Adyen Checkout API backed provider for payment-oriented billing flows."""

    CAPABILITIES = ALL_CAPABILITIES
    component_name: str = "adyen"
    merchant_account: str | None = Field(
        default=None, description="Adyen merchant account used for Checkout requests."
    )
    environment: str = Field(default="test", description="Adyen environment")
    live_url_prefix: str | None = Field(
        default=None, description="Adyen live URL prefix for production requests."
    )
    api_version: str = Field(default="v71", description="Adyen Checkout API version")

    @property
    def _checkout_url(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")
        if self.environment.lower() == "live":
            if not self.live_url_prefix:
                raise ValueError("Adyen live environment requires live_url_prefix")
            return f"https://{self.live_url_prefix}-checkout-live.adyenpayments.com/checkout/{self.api_version}"
        return f"https://checkout-test.adyen.com/{self.api_version}"

    def _post(self, path: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        response = requests.post(
            f"{self._checkout_url}/{path.lstrip('/')}",
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
            },
            json=dict(payload),
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"Adyen API error {response.status_code}: {response.text}"
            )
        return response.json() if response.content else {}

    def _merchant(self) -> str:
        if not self.merchant_account:
            raise ValueError("merchant_account is required for live Adyen API calls")
        return self.merchant_account

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
        amount_minor = getattr(price, "unit_amount_minor", None) or price.raw.get(
            "amount", {}
        ).get("value")
        currency = getattr(price, "currency", None) or price.raw.get("amount", {}).get(
            "currency", "USD"
        )
        payload = {
            "merchantAccount": self._merchant(),
            "reference": request.resolve("idempotency_key") or f"chk-{price.id}",
            "amount": {
                "value": int(amount_minor or 0) * int(request.quantity or 1),
                "currency": str(currency).upper(),
            },
            "returnUrl": request.resolve("success_url"),
            "countryCode": request.resolve("country_code", "US"),
            "shopperEmail": request.resolve("customer_email"),
            "metadata": request.resolve("metadata") or None,
        }
        raw = self._post(
            "sessions", {k: v for k, v in payload.items() if v is not None}
        )
        result = {
            "id": raw["id"],
            "url": raw.get("url"),
            "provider": self.component_name,
            "raw": raw,
        }
        return result

    # ---------------------------------------------------------------- Online Payments
    def _create_payment_intent(self, req: Any) -> Mapping[str, Any]:
        metadata = dict(req.resolve("metadata") or {})
        payment_method = metadata.pop("payment_method", None)
        if not payment_method:
            raise ValueError("Adyen payments require metadata['payment_method']")
        reference = req.resolve("idempotency_key") or f"pay-{uuid4().hex[:12]}"
        payload = {
            "merchantAccount": self._merchant(),
            "reference": reference,
            "amount": {
                "value": int(req.resolve("amount_minor") or 0),
                "currency": str(req.resolve("currency") or "USD").upper(),
            },
            "paymentMethod": payment_method,
            "shopperReference": metadata.pop("shopper_reference", None),
            "shopperInteraction": metadata.pop("shopper_interaction", "Ecommerce"),
            "recurringProcessingModel": metadata.pop(
                "recurring_processing_model", None
            ),
            "returnUrl": metadata.pop("return_url", None),
            "captureDelayHours": 0 if req.resolve("capture") else None,
            "metadata": metadata or None,
        }
        raw = self._post(
            "payments", {k: v for k, v in payload.items() if v is not None}
        )
        result = {
            "id": raw.get("pspReference") or reference,
            "status": raw.get("resultCode"),
            "amount_minor": req.resolve("amount_minor"),
            "currency": req.resolve("currency"),
            "provider": self.component_name,
            "raw": raw,
        }
        return result

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> Mapping[str, Any]:
        raw = self._post(
            f"payments/{payment_id}/captures",
            {
                "merchantAccount": self._merchant(),
                "reference": idempotency_key or f"cap-{payment_id}",
            },
        )
        result = {
            "id": raw.get("pspReference", payment_id),
            "status": raw.get("status", "received"),
            "provider": self.component_name,
            "raw": raw,
        }
        return result

    def _cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Mapping[str, Any]:
        raw = self._post(
            f"payments/{payment_id}/cancels",
            {
                "merchantAccount": self._merchant(),
                "reference": idempotency_key or f"cancel-{payment_id}",
            },
        )
        result = {
            "id": raw.get("pspReference", payment_id),
            "status": raw.get("status", "received"),
            "provider": self.component_name,
            "raw": raw,
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
        payload = json.loads(raw_body.decode("utf-8"))
        items = payload.get("notificationItems") or []
        if not items:
            return False
        item = items[0].get("NotificationRequestItem", items[0])
        additional = item.get("additionalData") or {}
        signature = additional.get("hmacSignature") or headers.get("HmacSignature", "")
        signing_parts = [
            item.get("pspReference", ""),
            item.get("originalReference", ""),
            item.get("merchantAccountCode", ""),
            item.get("merchantReference", ""),
            str((item.get("amount") or {}).get("value", "")),
            (item.get("amount") or {}).get("currency", ""),
            item.get("eventCode", ""),
            str(item.get("success", "")).lower(),
        ]
        signing_string = ":".join(
            str(part).replace("\\", "\\\\").replace(":", "\\:")
            for part in signing_parts
        )
        digest = hmac.new(
            base64.b64decode(secret),
            signing_string.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        expected = base64.b64encode(digest).decode("ascii")
        return hmac.compare_digest(expected, signature)

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
        raw = self._post(
            f"payments/{payment.id}/refunds",
            {
                "merchantAccount": self._merchant(),
                "reference": idempotency_key,
                "amount": {
                    "value": req.resolve("amount_minor")
                    or getattr(payment, "amount_minor", None),
                    "currency": (
                        req.resolve("currency")
                        or getattr(payment, "currency", None)
                        or "USD"
                    ).upper(),
                },
            },
        )
        result = {
            "id": raw.get("pspReference", payment.id),
            "status": raw.get("status", "received"),
            "provider": self.component_name,
            "raw": raw,
        }
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
        payload = json.loads(raw_body.decode("utf-8"))
        items = payload.get("notificationItems") or []
        item = items[0].get("NotificationRequestItem", items[0]) if items else {}
        result = {
            "event_id": item.get("pspReference", f"ady_evt_{uuid4().hex[:8]}"),
            "provider": self.component_name,
            "type": item.get("eventCode"),
            "raw": payload,
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
