"""Razorpay billing provider built on the shared billing base."""

from __future__ import annotations

from typing import Any, Mapping, Optional
from uuid import uuid4

from swarmauri_base.billing import BillingProviderBase
from swarmauri_core.billing.interfaces import ALL_CAPABILITIES, Operation


class RazorpayBillingProvider(BillingProviderBase):
    """Community provider stub echoing Razorpay style responses."""

    component_name: str = "razorpay"
    key_id: Optional[str] = None
    key_secret: Optional[str] = None
    CAPABILITIES = ALL_CAPABILITIES

    def _dispatch(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str],
    ) -> Any:
        """Return deterministic demo payloads for Razorpay operations."""

        if operation is Operation.VERIFY_WEBHOOK_SIGNATURE:
            return True
        if operation is Operation.LIST_DISPUTES:
            return [
                {
                    "id": f"rzp_{uuid4().hex[:12]}",
                    "provider": self.component_name,
                    "status": "opened",
                },
            ]
        if operation is Operation.PARSE_EVENT:
            return {
                "event_id": f"rzp_evt_{uuid4().hex[:12]}",
                "provider": self.component_name,
                "type": "payment.captured",
            }

        return {
            "id": f"{operation.value}_{uuid4().hex[:10]}",
            "provider": self.component_name,
            "echo": {
                "operation": operation.value,
                "payload": {k: str(v) for k, v in payload.items()},
                "idempotency_key": idempotency_key,
                "key_id": self.key_id,
            },
        }


__all__ = ["RazorpayBillingProvider"]
