"""Authorize.Net billing provider for the Swarmauri SDK."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Mapping, Optional, Sequence, cast
from uuid import uuid4

import requests
from pydantic import Field

from swarmauri_base.billing import (
    BillingProviderBase,
    CustomersMixin,
    OnlinePaymentsMixin,
    PaymentMethodsMixin,
    RefundsMixin,
    ReportsMixin,
    RiskMixin,
    WebhooksMixin,
)
from swarmauri_core.billing import Capability


class AuthorizeNetBillingProvider(
    OnlinePaymentsMixin,
    RefundsMixin,
    CustomersMixin,
    PaymentMethodsMixin,
    ReportsMixin,
    RiskMixin,
    WebhooksMixin,
    BillingProviderBase,
):
    """Authorize.Net JSON API provider focusing on card transaction workflows."""

    CAPABILITIES = frozenset(
        {
            Capability.ONLINE_PAYMENTS,
            Capability.REFUNDS,
            Capability.CUSTOMERS,
            Capability.PAYMENT_METHODS,
            Capability.REPORTS,
            Capability.RISK,
            Capability.WEBHOOKS,
        }
    )
    component_name: str = "authorize_net"
    login_id: str | None = Field(
        default=None, description="Authorize.Net API login ID."
    )
    environment: str = Field(default="sandbox", description="Authorize.Net environment")

    @property
    def _endpoint(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")
        if self.environment.lower() == "production":
            return "https://api.authorize.net/xml/v1/request.api"
        return "https://apitest.authorize.net/xml/v1/request.api"

    def _merchant_auth(self) -> Mapping[str, str]:
        if not self.login_id:
            raise ValueError("login_id is required for Authorize.Net API calls")
        return {
            "name": self.login_id,
            "transactionKey": self.api_key,
        }

    def _post(self, request_name: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        body = {
            request_name: {
                "merchantAuthentication": self._merchant_auth(),
                **dict(payload),
            }
        }
        response = requests.post(
            self._endpoint,
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"Authorize.Net API error {response.status_code}: {response.text}"
            )
        raw = response.content.decode("utf-8-sig")
        data = json.loads(raw)
        result = data.get(request_name.replace("Request", "Response"), data)
        messages = result.get("messages", {})
        if messages.get("resultCode") == "Error":
            raise RuntimeError(str(messages.get("message", result)))
        return result

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

    # ----------------------------------------------------------- online payments
    def _create_payment_intent(self, req: Any) -> Mapping[str, Any]:
        amount = int(req.resolve("amount_minor") or 0)
        currency = (req.resolve("currency") or "USD").upper()
        metadata = dict(req.resolve("metadata") or {})
        payment = metadata.get("payment") or metadata.get("opaque_data")
        if not payment:
            raise ValueError(
                "Authorize.Net payments require metadata['payment'] or metadata['opaque_data']"
            )
        if "dataDescriptor" in payment or "dataValue" in payment:
            payment_payload = {"opaqueData": payment}
        else:
            payment_payload = payment
        raw = self._post(
            "createTransactionRequest",
            {
                "transactionRequest": {
                    "transactionType": "authCaptureTransaction"
                    if req.resolve("capture")
                    else "authOnlyTransaction",
                    "amount": f"{amount / 100:.2f}",
                    "payment": payment_payload,
                    "currencyCode": currency,
                    "order": {"invoiceNumber": req.resolve("idempotency_key")}
                    if req.resolve("idempotency_key")
                    else None,
                }
            },
        )
        transaction = raw.get("transactionResponse", {})
        return {
            "id": str(transaction.get("transId") or uuid4().hex),
            "status": transaction.get("responseCode"),
            "amount_minor": amount,
            "currency": currency,
            "provider": self.component_name,
            "raw": raw,
        }

    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> Mapping[str, Any]:
        raw = self._post(
            "createTransactionRequest",
            {
                "transactionRequest": {
                    "transactionType": "priorAuthCaptureTransaction",
                    "refTransId": payment_id,
                }
            },
        )
        transaction = raw.get("transactionResponse", {})
        return {
            "id": str(transaction.get("transId") or payment_id),
            "status": transaction.get("responseCode"),
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
        raw = self._post(
            "createTransactionRequest",
            {
                "transactionRequest": {
                    "transactionType": "voidTransaction",
                    "refTransId": payment_id,
                }
            },
        )
        transaction = raw.get("transactionResponse", {})
        return {
            "id": str(transaction.get("transId") or payment_id),
            "status": transaction.get("responseCode"),
            "provider": self.component_name,
            "raw": raw,
        }

    # --------------------------------------------------------------------- refund
    def _create_refund(
        self, payment: Any, req: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        metadata = dict(req.resolve("metadata") or {})
        payment_payload = metadata.get("payment") or metadata.get("credit_card")
        if not payment_payload:
            raise ValueError("Authorize.Net refunds require payment card metadata")
        raw = self._post(
            "createTransactionRequest",
            {
                "transactionRequest": {
                    "transactionType": "refundTransaction",
                    "amount": f"{int(req.resolve('amount_minor') or 0) / 100:.2f}",
                    "payment": payment_payload,
                    "refTransId": getattr(payment, "id", ""),
                }
            },
        )
        transaction = raw.get("transactionResponse", {})
        return {
            "id": str(transaction.get("transId") or uuid4().hex),
            "status": transaction.get("responseCode"),
            "provider": self.component_name,
            "raw": raw,
        }

    def _get_refund(self, refund_id: str) -> Mapping[str, Any]:
        raw = self._post(
            "getTransactionDetailsRequest",
            {"transId": refund_id},
        )
        return {
            "id": refund_id,
            "status": raw.get("transaction", {}).get("transactionStatus"),
            "provider": self.component_name,
            "raw": raw,
        }

    # ------------------------------------------------------------------- customer
    def _create_customer(self, spec: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        raw = self._post(
            "createCustomerProfileRequest",
            {
                "profile": {
                    "merchantCustomerId": idempotency_key,
                    "description": spec.resolve("name", ""),
                    "email": spec.resolve("email"),
                }
            },
        )
        return {
            "id": str(raw.get("customerProfileId") or uuid4().hex),
            "provider": self.component_name,
            "raw": raw,
        }

    def _get_customer(self, customer_id: str) -> Mapping[str, Any]:
        raw = self._post(
            "getCustomerProfileRequest",
            {"customerProfileId": customer_id},
        )
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
        return {
            "id": f"anet_pm_{uuid4().hex[:10]}",
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
        payment_type = type or "credit_card"
        methods = []
        for index in range(min(limit, 3)):
            methods.append(
                {
                    "id": f"anet_pm_{index}",
                    "provider": self.component_name,
                    "type": payment_type,
                    "raw": self._stub(
                        "list_payment_methods",
                        customer_id=getattr(customer, "id", ""),
                        type=payment_type,
                        limit=limit,
                    ),
                }
            )
        return methods

    # --------------------------------------------------------------------- reports
    def _create_report(self, req: Any, *, idempotency_key: str) -> Mapping[str, Any]:
        return {
            "report_id": f"anet_report_{uuid4().hex[:10]}",
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
        signature = headers.get("X-ANET-Signature", "")
        if signature.lower().startswith("sha512="):
            signature = signature.split("=", 1)[1]
        digest = hmac.new(
            bytes.fromhex(secret),
            raw_body,
            hashlib.sha512,
        ).hexdigest()
        return hmac.compare_digest(digest.upper(), signature.upper())

    def _list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        if limit <= 0:
            return tuple()
        return (
            {
                "id": "anet_dispute_0",
                "status": "UNDER_REVIEW",
                "provider": self.component_name,
                "raw": self._stub("list_disputes"),
            },
        )

    # --------------------------------------------------------------------- webhooks
    def _parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> Mapping[str, Any]:
        payload = json.loads(raw_body.decode("utf-8"))
        event_type = payload.get("eventType") or headers.get(
            "X-ANET-Event-Type", "authorize_net.event"
        )
        return {
            "event_id": payload.get("notificationId", f"anet_evt_{uuid4().hex[:10]}"),
            "type": event_type,
            "provider": self.component_name,
            "raw": payload,
        }


__all__ = ["AuthorizeNetBillingProvider"]
