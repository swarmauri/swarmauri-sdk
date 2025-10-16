"""Stripe billing provider built on top of the shared billing base."""

from __future__ import annotations

from typing import Any, Mapping, Optional
from uuid import uuid4

from swarmauri_base.billing import BillingProviderBase
from swarmauri_core.billing.interfaces import ALL_CAPABILITIES, Operation


class StripeBillingProvider(BillingProviderBase):
    """Concrete provider stub demonstrating the dispatch contract for Stripe."""

    component_name: str = "stripe"
    CAPABILITIES = ALL_CAPABILITIES

    def _dispatch(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str],
    ) -> Any:
        """Demo dispatch that echoes the request in a deterministic shape."""

        if operation is Operation.VERIFY_WEBHOOK_SIGNATURE:
            return True
        if operation is Operation.LIST_DISPUTES:
            return [
                {
                    "id": f"dp_{uuid4().hex[:12]}",
                    "provider": self.component_name,
                    "status": "needs_response",
                },
                {
                    "id": f"dp_{uuid4().hex[:12]}",
                    "provider": self.component_name,
                    "status": "won",
                },
            ]
        if operation is Operation.PARSE_EVENT:
            return {
                "event_id": f"evt_{uuid4().hex[:12]}",
                "provider": self.component_name,
                "type": "payment_intent.succeeded",
            }

        return {
            "id": f"{operation.value}_{uuid4().hex[:10]}",
            "provider": self.component_name,
            "echo": {
                "operation": operation.value,
                "payload": {k: str(v) for k, v in payload.items()},
                "idempotency_key": idempotency_key,
            },
        }


__all__ = ["StripeBillingProvider"]
