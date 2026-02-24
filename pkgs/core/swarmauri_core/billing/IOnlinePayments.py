"""Online payments (payment intent) interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .protos import PaymentIntentReqProto, PaymentRefProto


class IOnlinePayments(ABC):
    """Operations for managing payment intents."""

    @abstractmethod
    def create_payment_intent(self, req: PaymentIntentReqProto) -> PaymentRefProto:
        """Create a payment intent."""

    @abstractmethod
    def capture_payment(
        self, payment_id: str, *, idempotency_key: Optional[str] = None
    ) -> PaymentRefProto:
        """Capture a payment intent."""

    @abstractmethod
    def cancel_payment(
        self,
        payment_id: str,
        *,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PaymentRefProto:
        """Cancel a payment intent."""
