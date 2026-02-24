"""Promotion and coupon interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from .protos import CouponSpecProto, PromotionSpecProto


class IPromotions(ABC):
    """Operations for managing promotions."""

    @abstractmethod
    def create_coupon(
        self, spec: CouponSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a coupon."""

    @abstractmethod
    def create_promotion(
        self, spec: PromotionSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a promotion."""
