"""Adyen billing provider built on the shared billing base."""

from __future__ import annotations

from typing import Any, Mapping, Optional
from uuid import uuid4

from swarmauri_base.billing import BillingProviderBase
from swarmauri_core.billing.interfaces import ALL_CAPABILITIES, Operation


class AdyenBillingProvider(BillingProviderBase):
    """Community provider stub echoing Adyen style responses."""

    component_name: str = "adyen"
    api_key: Optional[str] = None
    CAPABILITIES = ALL_CAPABILITIES

    def _dispatch(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str],
    ) -> Any:
        """Return deterministic demo payloads for Adyen operations."""

        if operation is Operation.VERIFY_WEBHOOK_SIGNATURE:
            return True
        if operation is Operation.LIST_DISPUTES:
            return [
                {
                    "id": f"ady_{uuid4().hex[:12]}",
                    "provider": self.component_name,
                    "status": "in_progress",
                },
            ]
        if operation is Operation.PARSE_EVENT:
            return {
                "event_id": f"ady_evt_{uuid4().hex[:12]}",
                "provider": self.component_name,
                "type": "AUTHORISATION",
            }

        return {
            "id": f"{operation.value}_{uuid4().hex[:10]}",
            "provider": self.component_name,
            "echo": {
                "operation": operation.value,
                "payload": {k: str(v) for k, v in payload.items()},
                "idempotency_key": idempotency_key,
                "api_key_set": bool(self.api_key),
            },
        }


__all__ = ["AdyenBillingProvider"]
