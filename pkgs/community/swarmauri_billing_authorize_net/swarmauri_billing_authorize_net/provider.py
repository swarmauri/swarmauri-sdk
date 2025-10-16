"""Authorize.Net billing provider stub for the Swarmauri SDK."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, cast
from uuid import uuid4

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
    """Stubbed Authorize.Net provider focusing on card transaction workflows."""

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
        return {
            "id": f"anet_txn_{uuid4().hex[:10]}",
            "status": "AUTHORIZED" if req.resolve("confirm") else "PENDING_REVIEW",
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

    # --------------------------------------------------------------------- refund
    def _create_refund(
        self, payment: Any, req: Any, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        return {
            "id": f"anet_refund_{uuid4().hex[:10]}",
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
            "id": f"anet_customer_{uuid4().hex[:10]}",
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
        return bool(signature and secret)

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
        event_type = headers.get("X-ANET-Event-Type", "authorize_net.event")
        return {
            "event_id": f"anet_evt_{uuid4().hex[:10]}",
            "type": event_type,
            "provider": self.component_name,
            "raw": self._stub(
                "parse_event",
                headers=dict(headers),
                raw_body=raw_body.decode("utf-8", errors="ignore"),
            ),
        }


__all__ = ["AuthorizeNetBillingProvider"]
