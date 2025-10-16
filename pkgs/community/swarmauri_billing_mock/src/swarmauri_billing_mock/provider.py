"""Mock billing provider built on the shared billing base."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from swarmauri_base.billing import BillingProviderBase
from swarmauri_core.billing.interfaces import ALL_CAPABILITIES, Operation


class MockBillingProvider(BillingProviderBase):
    """Deterministic billing provider useful for tests."""

    component_name: str = "mock"
    CAPABILITIES = ALL_CAPABILITIES

    def _dispatch(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str],
    ) -> Any:
        """Return predictable payloads for every supported operation."""

        if operation is Operation.VERIFY_WEBHOOK_SIGNATURE:
            return True
        if operation is Operation.LIST_DISPUTES:
            return [
                {"id": "mock_dispute", "provider": self.component_name, "status": "won"}
            ]
        if operation is Operation.PARSE_EVENT:
            return {
                "event_id": "mock_evt",
                "provider": self.component_name,
                "type": "test.event",
            }

        return {
            "id": f"mock_{operation.value}",
            "provider": self.component_name,
            "payload": payload,
            "idempotency_key": idempotency_key,
        }


__all__ = ["MockBillingProvider"]
