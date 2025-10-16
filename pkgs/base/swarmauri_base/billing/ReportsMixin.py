"""Mixin for reporting operations."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing import IReports
from swarmauri_core.billing.protos import ReportReqProto

from .utils import require_idempotency


class ReportsMixin(BaseModel, IReports):
    """Helper utilities for generating provider reports."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def create_report(
        self, req: ReportReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        require_idempotency(idempotency_key)
        return self._create_report(req, idempotency_key=idempotency_key)

    @abstractmethod
    def _create_report(
        self, req: ReportReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Trigger report generation with the provider."""


__all__ = ["ReportsMixin"]
