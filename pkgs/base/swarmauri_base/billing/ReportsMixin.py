"""Mixin for reporting operations."""

from __future__ import annotations

from typing import Any, Mapping, cast

from swarmauri_core.billing import IReports, Operation
from swarmauri_core.billing.protos import ReportReqProto

from .OperationDispatcherMixin import OperationDispatcherMixin


class ReportsMixin(OperationDispatcherMixin, IReports):
    """Delegates report generation to ``_op``."""

    def create_report(
        self, req: ReportReqProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        result = self._op(
            Operation.CREATE_REPORT,
            {"req": req},
            idempotency_key=idempotency_key,
        )
        return cast(Mapping[str, Any], result)


__all__ = ["ReportsMixin"]
