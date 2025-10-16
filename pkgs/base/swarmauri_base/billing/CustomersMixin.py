"""Mixin for customer management operations."""

from __future__ import annotations

from typing import Any, Mapping, cast

from swarmauri_core.billing import ICustomers, Operation
from swarmauri_core.billing.protos import (
    CustomerRefProto,
    CustomerSpecProto,
    PaymentMethodRefProto,
)

from .OperationDispatcherMixin import OperationDispatcherMixin, extract_raw_payload
from .refs import CustomerRef


class CustomersMixin(OperationDispatcherMixin, ICustomers):
    """Delegates customer CRUD operations."""

    def create_customer(
        self, spec: CustomerSpecProto, *, idempotency_key: str
    ) -> CustomerRefProto:
        self._require_idempotency(idempotency_key)
        result = self._op(
            Operation.CREATE_CUSTOMER,
            {"spec": spec},
            idempotency_key=idempotency_key,
        )
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
        result = self._op(Operation.GET_CUSTOMER, {"customer_id": customer_id})
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
        result = self._op(
            Operation.ATTACH_PM_TO_CUSTOMER,
            {"customer": customer, "payment_method": pm},
        )
        return cast(Mapping[str, Any], result)


__all__ = ["CustomersMixin"]
