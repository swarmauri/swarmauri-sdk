"""Mixin implementing balance and transfer operations."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping, cast

from swarmauri_core.billing import IBalanceTransfers
from swarmauri_core.billing.protos import BalanceRefProto, TransferReqProto

from .OperationDispatcherMixin import OperationDispatcherMixin, extract_raw_payload
from .refs import BalanceRef


class BalanceTransfersMixin(OperationDispatcherMixin, IBalanceTransfers):
    """Provides helpers for balance retrieval and transfers."""

    def get_balance(self) -> BalanceRefProto:
        result = self._get_balance()
        if isinstance(result, BalanceRefProto):
            return result
        raw = cast(Mapping[str, Any], result)
        payload = extract_raw_payload(raw)
        return BalanceRef(
            snapshot_id=str(raw.get("snapshot_id", "")),
            provider=str(raw.get("provider", "")),
            raw=payload,
        )

    def create_transfer(
        self, req: TransferReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        result = self._create_transfer(req, idempotency_key=idempotency_key)
        return cast(Mapping[str, Any], result)

    @abstractmethod
    def _get_balance(self) -> BalanceRefProto | Mapping[str, Any]:
        """Return the provider-specific balance payload."""

    @abstractmethod
    def _create_transfer(
        self, req: TransferReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a transfer using the underlying provider API."""


__all__ = ["BalanceTransfersMixin"]
