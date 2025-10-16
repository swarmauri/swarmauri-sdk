"""Compatibility imports for billing mixins."""

from __future__ import annotations

from typing import Tuple, Type

from pydantic import BaseModel

from .BalanceTransfersMixin import BalanceTransfersMixin
from .CustomersMixin import CustomersMixin
from .HostedCheckoutMixin import HostedCheckoutMixin
from .InvoicingMixin import InvoicingMixin
from .MarketplaceMixin import MarketplaceMixin
from .OnlinePaymentsMixin import OnlinePaymentsMixin
from .OperationDispatcherMixin import OperationDispatcherMixin
from .PaymentMethodsMixin import PaymentMethodsMixin
from .PayoutsMixin import PayoutsMixin
from .ProductsPricesMixin import ProductsPricesMixin
from .PromotionsMixin import PromotionsMixin
from .RefundsMixin import RefundsMixin
from .ReportsMixin import ReportsMixin
from .RiskMixin import RiskMixin
from .SubscriptionsMixin import SubscriptionsMixin
from .WebhooksMixin import WebhooksMixin

BillingMixins: Tuple[Type[BaseModel], ...] = (
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
)
"""Convenience tuple with all mixin classes."""

__all__ = [
    "BalanceTransfersMixin",
    "BillingMixins",
    "CustomersMixin",
    "HostedCheckoutMixin",
    "InvoicingMixin",
    "MarketplaceMixin",
    "OnlinePaymentsMixin",
    "OperationDispatcherMixin",
    "PaymentMethodsMixin",
    "PayoutsMixin",
    "ProductsPricesMixin",
    "PromotionsMixin",
    "RefundsMixin",
    "ReportsMixin",
    "RiskMixin",
    "SubscriptionsMixin",
    "WebhooksMixin",
]
