"""Mixin for online payment operations."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping, Optional, cast

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing import IOnlinePayments
from swarmauri_core.billing.protos import PaymentIntentReqProto, PaymentRefProto

from .utils import extract_raw_payload
from .refs import PaymentRef


class OnlinePaymentsMixin(BaseModel, IOnlinePayments):
    """Utility methods for common payment intent workflows."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def create_payment_intent(self, req: PaymentIntentReqProto) -> PaymentRefProto:
        result = self._create_payment_intent(req)
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
        result = self._capture_payment(payment_id, idempotency_key=idempotency_key)
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
        result = self._cancel_payment(
            payment_id, reason=reason, idempotency_key=idempotency_key
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

    @abstractmethod
    def _create_payment_intent(
        self, req: PaymentIntentReqProto
    ) -> PaymentRefProto | Mapping[str, Any]:
        """Create a payment intent with the provider."""

    @abstractmethod
    def _capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> PaymentRefProto | Mapping[str, Any]:
        """Capture a previously authorized payment."""

    @abstractmethod
    def _cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentRefProto | Mapping[str, Any]:
        """Cancel or void a payment intent."""


__all__ = ["OnlinePaymentsMixin"]
