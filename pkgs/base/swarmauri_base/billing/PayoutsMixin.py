"""Mixin for payout operations."""

from __future__ import annotations

from typing import Any, Mapping, cast

from swarmauri_core.billing import IPayouts, Operation
from swarmauri_core.billing.protos import PayoutReqProto

from .OperationDispatcherMixin import OperationDispatcherMixin


class PayoutsMixin(OperationDispatcherMixin, IPayouts):
    """Delegates payout creation to the provider implementation."""

    def create_payout(
        self, req: PayoutReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        result = self._op(
            Operation.CREATE_PAYOUT,
            {"req": req},
            idempotency_key=idempotency_key,
        )
        return cast(Mapping[str, Any], result)


__all__ = ["PayoutsMixin"]
