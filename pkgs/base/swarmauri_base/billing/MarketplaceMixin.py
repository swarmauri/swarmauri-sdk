"""Mixin for marketplace split operations."""

from __future__ import annotations

from typing import Any, Mapping, cast

from swarmauri_core.billing import IMarketplace, Operation
from swarmauri_core.billing.protos import SplitSpecProto

from .OperationDispatcherMixin import OperationDispatcherMixin


class MarketplaceMixin(OperationDispatcherMixin, IMarketplace):
    """Provides split creation and marketplace charge helpers."""

    def create_split(
        self, spec: SplitSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        result = self._op(
            Operation.CREATE_SPLIT,
            {"spec": spec},
            idempotency_key=idempotency_key,
        )
        return cast(Mapping[str, Any], result)

    def charge_with_split(
        self,
        amount_minor: int,
        currency: str,
        *,
        split_code_or_params: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        payload = {
            "amount_minor": amount_minor,
            "currency": currency,
            "split": split_code_or_params,
        }
        result = self._op(
            Operation.CHARGE_WITH_SPLIT,
            payload,
            idempotency_key=idempotency_key,
        )
        return cast(Mapping[str, Any], result)


__all__ = ["MarketplaceMixin"]
