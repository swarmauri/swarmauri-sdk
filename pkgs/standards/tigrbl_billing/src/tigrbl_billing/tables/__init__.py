# tigrbl_billing.tables – re-exports + autodiscovery helpers
from __future__ import annotations

import importlib
import pkgutil
from typing import Iterator

from tigrbl.table import Base as _Base  # Declarative base

# Explicit re-exports (keep these stable for static analyzers / IDEs)
from .product import Product
from .price import Price
from .price_tier import PriceTier
from .feature import Feature
from .price_feature_entitlement import PriceFeatureEntitlement
from .credit_usage_policy import CreditUsagePolicy
from .credit_ledger import CreditLedger
from .credit_grant import CreditGrant
from .balance_top_off import BalanceTopOff
from .customer_balance import CustomerBalance
from .customer import Customer
from .connected_account import ConnectedAccount
from .customer_account_link import CustomerAccountLink
from .subscription import Subscription
from .subscription_item import SubscriptionItem
from .seat_allocation import SeatAllocation
from .usage_event import UsageEvent
from .usage_rollup import UsageRollup
from .stripe_event_log import StripeEventLog, EventProcessStatus
from .webhook_endpoint import WebhookEndpoint

__all__ = [
    # Catalog
    "Product",
    "Price",
    "PriceTier",
    "Feature",
    "PriceFeatureEntitlement",
    # Credits
    "CreditUsagePolicy",
    "CreditLedger",
    "CreditGrant",
    "BalanceTopOff",
    "CustomerBalance",
    # Accounts
    "Customer",
    "ConnectedAccount",
    "CustomerAccountLink",
    "StripeEventLog",
    "EventProcessStatus",
    "WebhookEndpoint",
    # Subscriptions / Usage
    "Subscription",
    "SubscriptionItem",
    "SeatAllocation",
    "UsageEvent",
    "UsageRollup",
    # helpers
    "iter_models",
    "all_models",
    "by_tablename",
]


def _is_model(obj) -> bool:
    try:
        return (
            isinstance(obj, type)
            and issubclass(obj, _Base)
            and getattr(obj, "__abstract__", False) is not True
            and hasattr(obj, "__tablename__")
        )
    except Exception:
        return False


def iter_models() -> Iterator[type]:
    pkg = __name__
    for m in pkgutil.iter_modules(__path__, prefix=pkg + "."):
        if m.name.endswith(".__init__"):
            continue
        mod = importlib.import_module(m.name)
        for name in dir(mod):
            obj = getattr(mod, name, None)
            if _is_model(obj):
                yield obj


def all_models():
    return tuple(iter_models())


def by_tablename() -> dict:
    return {m.__tablename__: m for m in all_models()}


def __dir__():
    return sorted(__all__)


