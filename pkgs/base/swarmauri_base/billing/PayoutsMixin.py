"""Mixin for payout operations."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing import IPayouts
from swarmauri_core.billing.protos import PayoutReqProto

from .utils import require_idempotency


class PayoutsMixin(BaseModel, IPayouts):
    """Delegates payout creation to the provider implementation."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def create_payout(
        self, req: PayoutReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        require_idempotency(idempotency_key)
        return self._create_payout(req, idempotency_key=idempotency_key)

    @abstractmethod
    def _create_payout(
        self, req: PayoutReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Initiate a payout using the provider API."""


__all__ = ["PayoutsMixin"]
