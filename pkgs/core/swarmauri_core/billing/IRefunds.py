"""Refund interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from .protos import PaymentRefProto, RefundReqProto


class IRefunds(ABC):
    """Operations for managing refunds."""

    @abstractmethod
    def create_refund(
        self, payment: PaymentRefProto, req: RefundReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a refund."""

    @abstractmethod
    def get_refund(self, refund_id: str) -> Mapping[str, Any]:
        """Retrieve a refund."""
