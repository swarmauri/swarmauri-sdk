"""Subscription interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from .protos import SubscriptionSpecProto


class ISubscriptions(ABC):
    """Operations for managing subscriptions."""

    @abstractmethod
    def create_subscription(
        self, spec: SubscriptionSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a subscription."""

    @abstractmethod
    def cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        """Cancel a subscription."""
