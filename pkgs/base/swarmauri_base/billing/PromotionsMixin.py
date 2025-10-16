"""Mixin for coupon and promotion helpers."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from swarmauri_core.billing import IPromotions
from swarmauri_core.billing.protos import CouponSpecProto, PromotionSpecProto

from .OperationDispatcherMixin import OperationDispatcherMixin


class PromotionsMixin(OperationDispatcherMixin, IPromotions):
    """Delegates promotional resource creation."""

    def create_coupon(
        self, spec: CouponSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return self._create_coupon(spec, idempotency_key=idempotency_key)

    def create_promotion(
        self, spec: PromotionSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return self._create_promotion(spec, idempotency_key=idempotency_key)

    @abstractmethod
    def _create_coupon(
        self, spec: CouponSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a coupon with the provider."""

    @abstractmethod
    def _create_promotion(
        self, spec: PromotionSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a promotion with the provider."""


__all__ = ["PromotionsMixin"]
