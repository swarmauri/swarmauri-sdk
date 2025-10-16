"""Mixin for reporting operations."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from swarmauri_core.billing import IReports
from swarmauri_core.billing.protos import ReportReqProto

from .OperationDispatcherMixin import OperationDispatcherMixin


class ReportsMixin(OperationDispatcherMixin, IReports):
    """Helper utilities for generating provider reports."""

    def create_report(
        self, req: ReportReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return self._create_report(req, idempotency_key=idempotency_key)

    @abstractmethod
    def _create_report(
        self, req: ReportReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Trigger report generation with the provider."""


__all__ = ["ReportsMixin"]
