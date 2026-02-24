"""Balance transfer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from .protos import BalanceRefProto, TransferReqProto


class IBalanceTransfers(ABC):
    """Operations for balance retrieval and transfers."""

    @abstractmethod
    def get_balance(self) -> BalanceRefProto:
        """Retrieve the provider balance."""

    @abstractmethod
    def create_transfer(
        self, req: TransferReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a balance transfer."""
