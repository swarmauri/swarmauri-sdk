"""Mixin for coupon and promotion helpers."""

from __future__ import annotations

from typing import Any, Mapping, cast

from swarmauri_core.billing import IPromotions, Operation
from swarmauri_core.billing.protos import CouponSpecProto, PromotionSpecProto

from .OperationDispatcherMixin import OperationDispatcherMixin


class PromotionsMixin(OperationDispatcherMixin, IPromotions):
    """Delegates promotional resource creation."""

    def create_coupon(
        self, spec: CouponSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        result = self._op(
            Operation.CREATE_COUPON,
            {"spec": spec},
            idempotency_key=idempotency_key,
        )
        return cast(Mapping[str, Any], result)

    def create_promotion(
        self, spec: PromotionSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        result = self._op(
            Operation.CREATE_PROMOTION,
            {"spec": spec},
            idempotency_key=idempotency_key,
        )
        return cast(Mapping[str, Any], result)


__all__ = ["PromotionsMixin"]
