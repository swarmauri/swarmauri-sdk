"""Mixin for customer management operations."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping, cast

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing import ICustomers
from swarmauri_core.billing.protos import (
    CustomerRefProto,
    CustomerSpecProto,
    PaymentMethodRefProto,
)

from .utils import extract_raw_payload, require_idempotency
from .refs import CustomerRef


class CustomersMixin(BaseModel, ICustomers):
    """Delegates customer CRUD operations."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def create_customer(
        self, spec: CustomerSpecProto, *, idempotency_key: str
    ) -> CustomerRefProto:
        require_idempotency(idempotency_key)
        result = self._create_customer(spec, idempotency_key=idempotency_key)
        if isinstance(result, CustomerRefProto):
            return result
        raw = cast(Mapping[str, Any], result)
        payload = extract_raw_payload(raw)
        return CustomerRef(
            id=str(raw.get("id", "")),
            provider=str(raw.get("provider", "")),
            raw=payload,
        )

    def get_customer(self, customer_id: str) -> CustomerRefProto:
        result = self._get_customer(customer_id)
        if isinstance(result, CustomerRefProto):
            return result
        raw = cast(Mapping[str, Any], result)
        payload = extract_raw_payload(raw)
        return CustomerRef(
            id=str(raw.get("id", customer_id)),
            provider=str(raw.get("provider", "")),
            raw=payload,
        )

    def attach_payment_method_to_customer(
        self, customer: CustomerRefProto, pm: PaymentMethodRefProto
    ) -> Mapping[str, Any]:
        result = self._attach_payment_method_to_customer(customer, pm)
        return cast(Mapping[str, Any], result)

    @abstractmethod
    def _create_customer(
        self, spec: CustomerSpecProto, *, idempotency_key: str
    ) -> CustomerRefProto | Mapping[str, Any]:
        """Create a customer via the provider and return its reference."""

    @abstractmethod
    def _get_customer(self, customer_id: str) -> CustomerRefProto | Mapping[str, Any]:
        """Return provider data for the requested customer."""

    @abstractmethod
    def _attach_payment_method_to_customer(
        self, customer: CustomerRefProto, pm: PaymentMethodRefProto
    ) -> Mapping[str, Any]:
        """Associate a payment method with the given customer."""


__all__ = ["CustomersMixin"]
