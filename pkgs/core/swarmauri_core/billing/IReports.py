"""Reporting interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from .protos import ReportReqProto


class IReports(ABC):
    """Operations for generating reports."""

    @abstractmethod
    def create_report(
        self, req: ReportReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create a report generation job."""
