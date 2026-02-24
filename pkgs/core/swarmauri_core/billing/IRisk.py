"""Risk and dispute interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence


class IRisk(ABC):
    """Risk management operations."""

    @abstractmethod
    def verify_webhook_signature(
        self, raw_body: bytes, headers: Mapping[str, str], secret: str
    ) -> bool:
        """Verify a webhook signature."""

    @abstractmethod
    def list_disputes(self, *, limit: int = 50) -> Sequence[Mapping[str, Any]]:
        """List disputes."""
