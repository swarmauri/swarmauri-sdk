"""Marketplace and split interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from .protos import SplitSpecProto


class IMarketplace(ABC):
    """Operations for marketplace splits and charges."""

    @abstractmethod
    def create_split(
        self, spec: SplitSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a split configuration."""

    @abstractmethod
    def charge_with_split(
        self,
        amount_minor: int,
        currency: str,
        *,
        split_code_or_params: Mapping[str, Any],
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        """Charge an amount while applying a split configuration."""
