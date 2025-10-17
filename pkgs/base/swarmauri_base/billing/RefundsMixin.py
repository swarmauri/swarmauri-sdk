"""Mixin for refund operations."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing import IRefunds
from swarmauri_core.billing.protos import PaymentRefProto, RefundReqProto

from .utils import require_idempotency


class RefundsMixin(IRefunds, BaseModel):
    """Delegates refund creation and retrieval."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def create_refund(
        self, payment: PaymentRefProto, req: RefundReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        require_idempotency(idempotency_key)
        return self._create_refund(payment, req, idempotency_key=idempotency_key)

    def get_refund(self, refund_id: str) -> Mapping[str, Any]:
        return self._get_refund(refund_id)

    @abstractmethod
    def _create_refund(
        self, payment: PaymentRefProto, req: RefundReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a refund using the provider API."""

    @abstractmethod
    def _get_refund(self, refund_id: str) -> Mapping[str, Any]:
        """Return provider data for the refund."""


__all__ = ["RefundsMixin"]
