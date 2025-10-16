"""Mixin wrapping subscription operations."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing import ISubscriptions
from swarmauri_core.billing.protos import SubscriptionSpecProto

from .utils import require_idempotency


class SubscriptionsMixin(BaseModel, ISubscriptions):
    """Delegates subscription operations to the provider implementation."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def create_subscription(
        self, spec: SubscriptionSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        require_idempotency(idempotency_key)
        return self._create_subscription(spec, idempotency_key=idempotency_key)

    def cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        return self._cancel_subscription(subscription_id, at_period_end=at_period_end)

    @abstractmethod
    def _create_subscription(
        self, spec: SubscriptionSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a subscription in the provider system."""

    @abstractmethod
    def _cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        """Cancel the subscription as requested."""


__all__ = ["SubscriptionsMixin"]
