"""Mixin wrapping subscription operations."""

from __future__ import annotations

from typing import Any, Mapping, cast

from swarmauri_core.billing import ISubscriptions, Operation
from swarmauri_core.billing.protos import SubscriptionSpecProto

from .OperationDispatcherMixin import OperationDispatcherMixin


class SubscriptionsMixin(OperationDispatcherMixin, ISubscriptions):
    """Delegates subscription operations to the provider implementation."""

    def create_subscription(
        self, spec: SubscriptionSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        result = self._op(
            Operation.CREATE_SUBSCRIPTION,
            {"spec": spec},
            idempotency_key=idempotency_key,
        )
        return cast(Mapping[str, Any], result)

    def cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> Mapping[str, Any]:
        result = self._op(
            Operation.CANCEL_SUBSCRIPTION,
            {"subscription_id": subscription_id, "at_period_end": at_period_end},
        )
        return cast(Mapping[str, Any], result)


__all__ = ["SubscriptionsMixin"]
