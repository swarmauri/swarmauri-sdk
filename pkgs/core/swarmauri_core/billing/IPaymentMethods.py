"""Payment method interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, Sequence

from .protos import CustomerRefProto, PaymentMethodRefProto, PaymentMethodSpecProto


class IPaymentMethods(ABC):
    """Operations for managing payment methods."""

    @abstractmethod
    def create_payment_method(
        self, spec: PaymentMethodSpecProto, *, idempotency_key: str
    ) -> PaymentMethodRefProto:
        """Create a payment method."""

    @abstractmethod
    def detach_payment_method(self, payment_method_id: str) -> Mapping[str, Any]:
        """Detach a payment method."""

    @abstractmethod
    def list_payment_methods(
        self,
        customer: CustomerRefProto,
        *,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> Sequence[PaymentMethodRefProto]:
        """List payment methods for a customer."""
