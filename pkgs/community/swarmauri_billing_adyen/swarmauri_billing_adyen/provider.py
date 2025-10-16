"""Concrete Adyen billing provider."""

from __future__ import annotations

from typing import Any, Mapping, Optional
from uuid import uuid4

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


class AdyenBillingProvider(
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
    """Example Adyen provider; replace ``_dispatch`` with real HTTP calls."""

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
                    "id": f"ady_{uuid4().hex[:12]}",
                    "provider": "adyen",
                    "status": "in_progress",
                },
            ]
        if operation is Operation.PARSE_EVENT:
            return {
                "event_id": f"ady_evt_{uuid4().hex[:12]}",
                "provider": "adyen",
                "type": "AUTHORISATION",
            }

        return {
            "id": f"ady_{operation.value}_{uuid4().hex[:10]}",
            "provider": "adyen",
            "echo": {
                "operation": operation.value,
                "payload_keys": list(payload.keys()),
                "idempotency_key": idempotency_key,
            },
        }
