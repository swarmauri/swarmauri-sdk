"""Base provider class composing all billing strategy mixins."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, FrozenSet, Mapping, Optional, Tuple, Type

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.billing.interfaces import (
    ALL_CAPABILITIES,
    Capability,
    IBillingProvider,
    Operation,
)

from .mixins import (
    BalanceTransfersMixin,
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
    ALL_API_STRATEGIES,
)


class BillingProviderBase(
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
    ComponentBase,
    IBillingProvider,
):
    """Concrete providers subclass this and implement :meth:`_dispatch`."""

    component_name: str = "billing_provider"
    CAPABILITIES: FrozenSet[Capability] = ALL_CAPABILITIES

    # Optional connection level configuration
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: float = 30.0

    @abstractmethod
    def _dispatch(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str],
    ) -> Any:
        """Providers implement the low level dispatch routine."""

    def _op(
        self,
        operation: Operation,
        payload: Mapping[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> Any:
        """Route mixin calls through the provider dispatch implementation."""

        return self._dispatch(operation, payload, idempotency_key=idempotency_key)

    @property
    def capabilities(self) -> FrozenSet[Capability]:
        """Expose supported capabilities."""

        return self.CAPABILITIES

    @property
    def api_strategies(self) -> Tuple[Type[Any], ...]:
        """Expose supported strategy interfaces."""

        return ALL_API_STRATEGIES


__all__ = ["BillingProviderBase"]
