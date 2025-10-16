"""Mixin for invoicing operations."""

from __future__ import annotations

from typing import Any, Mapping, cast

from swarmauri_core.billing import IInvoicing, Operation
from swarmauri_core.billing.protos import InvoiceSpecProto

from .OperationDispatcherMixin import OperationDispatcherMixin


class InvoicingMixin(OperationDispatcherMixin, IInvoicing):
    """Delegates invoice lifecycle calls to ``_op``."""

    def create_invoice(
        self, spec: InvoiceSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        result = self._op(
            Operation.CREATE_INVOICE,
            {"spec": spec},
            idempotency_key=idempotency_key,
        )
        return cast(Mapping[str, Any], result)

    def finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        result = self._op(Operation.FINALIZE_INVOICE, {"invoice_id": invoice_id})
        return cast(Mapping[str, Any], result)

    def void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        result = self._op(Operation.VOID_INVOICE, {"invoice_id": invoice_id})
        return cast(Mapping[str, Any], result)

    def mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        result = self._op(Operation.MARK_UNCOLLECTIBLE, {"invoice_id": invoice_id})
        return cast(Mapping[str, Any], result)


__all__ = ["InvoicingMixin"]
