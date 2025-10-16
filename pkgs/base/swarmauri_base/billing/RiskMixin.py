"""Mixin for risk-related billing operations."""

from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from swarmauri_core.billing import IRisk, Operation

from .OperationDispatcherMixin import OperationDispatcherMixin


class RiskMixin(OperationDispatcherMixin, IRisk):
    """Delegates webhook verification and dispute listing."""

    def verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        result = self._op(
            Operation.VERIFY_WEBHOOK_SIGNATURE,
            {"raw_body": raw_body, "headers": headers, "secret": secret},
        )
        return bool(result)

    def list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        result = self._op(Operation.LIST_DISPUTES, {"limit": limit})
        if isinstance(result, Sequence):
            return cast(Sequence[Mapping[str, Any]], result)
        if result is None:
            return tuple()
        return (cast(Mapping[str, Any], result),)


__all__ = ["RiskMixin"]
