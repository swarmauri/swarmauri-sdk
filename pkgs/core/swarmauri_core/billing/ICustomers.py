"""Customer management interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from .protos import CustomerRefProto, CustomerSpecProto, PaymentMethodRefProto


class ICustomers(ABC):
    """Operations for managing customers."""

    @abstractmethod
    def create_customer(
        self, spec: CustomerSpecProto, *, idempotency_key: str
    ) -> CustomerRefProto:
        """Create a customer profile."""

    @abstractmethod
    def get_customer(self, customer_id: str) -> CustomerRefProto:
        """Retrieve a customer profile."""

    @abstractmethod
    def attach_payment_method_to_customer(
        self, customer: CustomerRefProto, pm: PaymentMethodRefProto
    ) -> Mapping[str, Any]:
        """Attach a payment method to a customer."""
