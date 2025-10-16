"""Mixin providing payment method helpers."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Tuple, cast

from swarmauri_core.billing import IPaymentMethods, Operation
from swarmauri_core.billing.protos import (
    CustomerRefProto,
    PaymentMethodRefProto,
    PaymentMethodSpecProto,
)

from .OperationDispatcherMixin import OperationDispatcherMixin, extract_raw_payload
from .refs import PaymentMethodRef


class PaymentMethodsMixin(OperationDispatcherMixin, IPaymentMethods):
    """Delegates payment method management operations."""

    def create_payment_method(
        self, spec: PaymentMethodSpecProto, *, idempotency_key: str
    ) -> PaymentMethodRefProto:
        self._require_idempotency(idempotency_key)
        result = self._op(
            Operation.CREATE_PAYMENT_METHOD,
            {"spec": spec},
            idempotency_key=idempotency_key,
        )
        if isinstance(result, PaymentMethodRefProto):
            return result
        raw = cast(Mapping[str, Any], result)
        payload = extract_raw_payload(raw)
        return PaymentMethodRef(
            id=str(raw.get("id", "")),
            provider=str(raw.get("provider", "")),
            raw=payload,
        )

    def detach_payment_method(self, payment_method_id: str) -> Mapping[str, Any]:
        result = self._op(
            Operation.DETACH_PAYMENT_METHOD,
            {"payment_method_id": payment_method_id},
        )
        return cast(Mapping[str, Any], result)

    def list_payment_methods(
        self,
        customer: CustomerRefProto,
        *,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> Sequence[PaymentMethodRefProto]:
        result = self._op(
            Operation.LIST_PAYMENT_METHODS,
            {"customer": customer, "type": type, "limit": limit},
        )
        if isinstance(result, Sequence):
            items: Sequence[Any] = result
        else:
            items = (result,) if result is not None else tuple()
        refs: Tuple[PaymentMethodRefProto, ...] = tuple(
            item
            if isinstance(item, PaymentMethodRefProto)
            else PaymentMethodRef(
                id=str(cast(Mapping[str, Any], item).get("id", "")),
                provider=str(cast(Mapping[str, Any], item).get("provider", "")),
                raw=extract_raw_payload(cast(Mapping[str, Any], item)),
            )
            for item in items
        )
        return refs


__all__ = ["PaymentMethodsMixin"]
