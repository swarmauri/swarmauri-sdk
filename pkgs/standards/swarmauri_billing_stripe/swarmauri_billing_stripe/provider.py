"""Concrete Stripe billing provider."""

from __future__ import annotations

from typing import Any, Mapping, Optional
from uuid import uuid4

from swarmauri_base.billing import BillingProviderBase
from swarmauri_core.billing import ALL_CAPABILITIES, Operation


class StripeBillingProvider(BillingProviderBase):
    """Example Stripe provider; replace ``_dispatch`` with real HTTP calls."""

    CAPABILITIES = ALL_CAPABILITIES

    def _dispatch(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str],
    ) -> Any:
        if operation is Operation.VERIFY_WEBHOOK_SIGNATURE:
            return True
        if operation is Operation.LIST_DISPUTES:
            return [
                {
                    "id": f"dp_{uuid4().hex[:12]}",
                    "provider": "stripe",
                    "status": "needs_response",
                },
                {"id": f"dp_{uuid4().hex[:12]}", "provider": "stripe", "status": "won"},
            ]
        if operation is Operation.PARSE_EVENT:
            return {
                "event_id": f"evt_{uuid4().hex[:12]}",
                "provider": "stripe",
                "type": "payment_intent.succeeded",
            }

        return {
            "id": f"{operation.value}_{uuid4().hex[:10]}",
            "provider": "stripe",
            "echo": {
                "operation": operation.value,
                "payload": {k: str(v) for k, v in payload.items()},
                "idempotency_key": idempotency_key,
            },
        }
