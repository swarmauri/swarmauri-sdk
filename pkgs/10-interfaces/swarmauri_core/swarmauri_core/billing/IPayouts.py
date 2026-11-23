"""Payout interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from .protos import PayoutReqProto


class IPayouts(ABC):
    """Operations for creating payouts."""

    @abstractmethod
    def create_payout(
        self, req: PayoutReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a payout."""
