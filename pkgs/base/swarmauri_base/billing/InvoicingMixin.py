"""Mixin for invoicing operations."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping

from swarmauri_core.billing import IInvoicing
from swarmauri_core.billing.protos import InvoiceSpecProto

from .OperationDispatcherMixin import OperationDispatcherMixin


class InvoicingMixin(OperationDispatcherMixin, IInvoicing):
    """Shared invoice lifecycle helpers backed by provider hooks."""

    def create_invoice(
        self, spec: InvoiceSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        self._require_idempotency(idempotency_key)
        return self._create_invoice(spec, idempotency_key=idempotency_key)

    def finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        return self._finalize_invoice(invoice_id)

    def void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        return self._void_invoice(invoice_id)

    def mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        return self._mark_uncollectible(invoice_id)

    @abstractmethod
    def _create_invoice(
        self, spec: InvoiceSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create an invoice with the provider."""

    @abstractmethod
    def _finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        """Finalize the invoice and return provider response."""

    @abstractmethod
    def _void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        """Void the invoice with the provider."""

    @abstractmethod
    def _mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        """Mark the invoice as uncollectible with the provider."""


__all__ = ["InvoicingMixin"]
