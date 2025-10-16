"""Mixin for risk-related billing operations."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping, Sequence, cast

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing import IRisk


class RiskMixin(BaseModel, IRisk):
    """Delegates webhook verification and dispute listing."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        result = self._verify_webhook_signature(raw_body, headers, secret)
        return bool(result)

    def list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        result = self._list_disputes(limit=limit)
        if isinstance(result, Sequence):
            return cast(Sequence[Mapping[str, Any]], result)
        if result is None:
            return tuple()
        return (cast(Mapping[str, Any], result),)

    @abstractmethod
    def _verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool | Mapping[str, Any]:
        """Validate a webhook signature using the provider's algorithm."""

    @abstractmethod
    def _list_disputes(
        self, *, limit: int = 50
    ) -> Sequence[Mapping[str, Any]] | Mapping[str, Any] | None:
        """Return a collection of disputes from the provider."""


__all__ = ["RiskMixin"]
