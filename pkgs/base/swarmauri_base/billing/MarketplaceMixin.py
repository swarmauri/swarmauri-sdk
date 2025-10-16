"""Mixin for marketplace split operations."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing import IMarketplace
from swarmauri_core.billing.protos import SplitSpecProto

from .utils import require_idempotency


class MarketplaceMixin(BaseModel, IMarketplace):
    """Provides split creation and marketplace charge helpers."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def create_split(
        self, spec: SplitSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        require_idempotency(idempotency_key)
        return self._create_split(spec, idempotency_key=idempotency_key)

    def charge_with_split(
        self,
        amount_minor: int,
        currency: str,
        *,
        split_code_or_params: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        require_idempotency(idempotency_key)
        return self._charge_with_split(
            amount_minor,
            currency,
            split_code_or_params=split_code_or_params,
            idempotency_key=idempotency_key,
        )

    @abstractmethod
    def _create_split(
        self, spec: SplitSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a split configuration with the provider."""

    @abstractmethod
    def _charge_with_split(
        self,
        amount_minor: int,
        currency: str,
        *,
        split_code_or_params: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        """Execute a marketplace charge with split parameters."""


__all__ = ["MarketplaceMixin"]
