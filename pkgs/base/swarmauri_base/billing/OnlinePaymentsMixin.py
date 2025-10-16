"""Mixin for online payment operations."""

from __future__ import annotations

from typing import Any, Mapping, Optional, cast

from swarmauri_core.billing import IOnlinePayments, Operation
from swarmauri_core.billing.protos import PaymentIntentReqProto, PaymentRefProto

from .OperationDispatcherMixin import OperationDispatcherMixin, extract_raw_payload
from .refs import PaymentRef


class OnlinePaymentsMixin(OperationDispatcherMixin, IOnlinePayments):
    """Delegates payment intents and capture operations via ``_op``."""

    def create_payment_intent(self, req: PaymentIntentReqProto) -> PaymentRefProto:
        result = self._op(Operation.CREATE_PAYMENT_INTENT, {"req": req})
        if isinstance(result, PaymentRefProto):
            return result
        raw = cast(Mapping[str, Any], result)
        payload = extract_raw_payload(raw)
        return PaymentRef(
            id=str(raw.get("id", "")),
            status=str(raw.get("status", "")),
            provider=str(raw.get("provider", "")),
            raw=payload,
        )

    def capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> PaymentRefProto:
        result = self._op(
            Operation.CAPTURE_PAYMENT,
            {"payment_id": payment_id},
            idempotency_key=idempotency_key,
        )
        if isinstance(result, PaymentRefProto):
            return result
        raw = cast(Mapping[str, Any], result)
        payload = extract_raw_payload(raw)
        return PaymentRef(
            id=str(raw.get("id", payment_id)),
            status=str(raw.get("status", "")),
            provider=str(raw.get("provider", "")),
            raw=payload,
        )

    def cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentRefProto:
        result = self._op(
            Operation.CANCEL_PAYMENT,
            {"payment_id": payment_id, "reason": reason},
            idempotency_key=idempotency_key,
        )
        if isinstance(result, PaymentRefProto):
            return result
        raw = cast(Mapping[str, Any], result)
        payload = extract_raw_payload(raw)
        return PaymentRef(
            id=str(raw.get("id", payment_id)),
            status=str(raw.get("status", "")),
            provider=str(raw.get("provider", "")),
            raw=payload,
        )


__all__ = ["OnlinePaymentsMixin"]
