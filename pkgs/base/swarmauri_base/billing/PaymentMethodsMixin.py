"""Mixin providing payment method helpers."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping, Optional, Sequence, Tuple, cast

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing import IPaymentMethods
from swarmauri_core.billing.protos import (
    CustomerRefProto,
    PaymentMethodRefProto,
    PaymentMethodSpecProto,
)

from .utils import extract_raw_payload, require_idempotency
from .refs import PaymentMethodRef


class PaymentMethodsMixin(IPaymentMethods, BaseModel):
    """Delegates payment method management operations."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def create_payment_method(
        self, spec: PaymentMethodSpecProto, *, idempotency_key: str
    ) -> PaymentMethodRefProto:
        require_idempotency(idempotency_key)
        result = self._create_payment_method(spec, idempotency_key=idempotency_key)
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
        return self._detach_payment_method(payment_method_id)

    def list_payment_methods(
        self,
        customer: CustomerRefProto,
        *,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> Sequence[PaymentMethodRefProto]:
        result = self._list_payment_methods(customer, type=type, limit=limit)
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

    @abstractmethod
    def _create_payment_method(
        self, spec: PaymentMethodSpecProto, *, idempotency_key: str
    ) -> PaymentMethodRefProto | Mapping[str, Any]:
        """Create a new payment method with the provider."""

    @abstractmethod
    def _detach_payment_method(self, payment_method_id: str) -> Mapping[str, Any]:
        """Detach the given payment method from its customer."""

    @abstractmethod
    def _list_payment_methods(
        self,
        customer: CustomerRefProto,
        *,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> (
        Sequence[PaymentMethodRefProto]
        | Sequence[Mapping[str, Any]]
        | Mapping[str, Any]
        | None
    ):
        """List payment methods for the provided customer."""


__all__ = ["PaymentMethodsMixin"]
