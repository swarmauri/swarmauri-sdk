"""Mixin for refund operations."""

from __future__ import annotations

from typing import Any, Mapping, cast

from swarmauri_core.billing import IRefunds, Operation
from swarmauri_core.billing.protos import PaymentRefProto, RefundReqProto

from .OperationDispatcherMixin import OperationDispatcherMixin


class RefundsMixin(OperationDispatcherMixin, IRefunds):
    """Delegates refund creation and retrieval."""

    def create_refund(
        self, payment: PaymentRefProto, req: RefundReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        result = self._op(
            Operation.CREATE_REFUND,
            {"payment": payment, "req": req},
            idempotency_key=idempotency_key,
        )
        return cast(Mapping[str, Any], result)

    def get_refund(self, refund_id: str) -> Mapping[str, Any]:
        result = self._op(Operation.GET_REFUND, {"refund_id": refund_id})
        return cast(Mapping[str, Any], result)


__all__ = ["RefundsMixin"]
