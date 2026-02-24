"""Invoicing interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from .protos import InvoiceSpecProto


class IInvoicing(ABC):
    """Operations for managing invoices."""

    @abstractmethod
    def create_invoice(
        self, spec: InvoiceSpecProto, *, idempotency_key: str
    ) -> Mapping[str, Any]:
        """Create an invoice."""

    @abstractmethod
    def finalize_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        """Finalize an invoice for payment."""

    @abstractmethod
    def void_invoice(self, invoice_id: str) -> Mapping[str, Any]:
        """Void an invoice."""

    @abstractmethod
    def mark_uncollectible(self, invoice_id: str) -> Mapping[str, Any]:
        """Mark an invoice as uncollectible."""
