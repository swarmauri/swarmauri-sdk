"""Mock billing provider used in tests and examples."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from swarmauri_base.billing import (
    BalanceTransfersMixin,
    BillingProviderBase,
    CustomersMixin,
    HostedCheckoutMixin,
    InvoicingMixin,
    MarketplaceMixin,
    OnlinePaymentsMixin,
    PaymentMethodsMixin,
    PayoutsMixin,
    ProductsPricesMixin,
    PromotionsMixin,
    RefundsMixin,
    ReportsMixin,
    RiskMixin,
    SubscriptionsMixin,
    WebhooksMixin,
)
from swarmauri_core.billing import ALL_CAPABILITIES, Operation


class MockBillingProvider(
    ProductsPricesMixin,
    HostedCheckoutMixin,
    OnlinePaymentsMixin,
    SubscriptionsMixin,
    InvoicingMixin,
    MarketplaceMixin,
    RiskMixin,
    RefundsMixin,
    CustomersMixin,
    PaymentMethodsMixin,
    PayoutsMixin,
    BalanceTransfersMixin,
    ReportsMixin,
    WebhooksMixin,
    PromotionsMixin,
    BillingProviderBase,
):
    """Deterministic mock provider suitable for unit tests."""

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
            return [{"id": "mock_dispute_1", "provider": "mock", "status": "won"}]
        if operation is Operation.PARSE_EVENT:
            return {"event_id": "mock_evt_1", "provider": "mock", "type": "test.event"}

        return {
            "id": f"mock_{operation.value}",
            "provider": "mock",
            "payload": payload,
            "idempotency_key": idempotency_key,
        }
