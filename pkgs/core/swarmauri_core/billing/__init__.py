"""Billing interfaces exposed to provider implementations."""

from __future__ import annotations

from abc import ABC
from typing import Tuple, Type

from .IBalanceTransfers import IBalanceTransfers
from .IBillingProvider import IBillingProvider
from .ICustomers import ICustomers
from .IHostedCheckout import IHostedCheckout
from .IInvoicing import IInvoicing
from .IMarketplace import IMarketplace
from .IOnlinePayments import IOnlinePayments
from .IPaymentMethods import IPaymentMethods
from .IPayouts import IPayouts
from .IPromotions import IPromotions
from .IProductsPrices import IProductsPrices
from .IRefunds import IRefunds
from .IReports import IReports
from .IRisk import IRisk
from .ISubscriptions import ISubscriptions
from .IWebhooks import IWebhooks
from .enums import (
    ALL_CAPABILITIES,
    CAPABILITY_TO_TIGRBL,
    Capability,
    Operation,
    capabilities_to_tigrbl,
)
from .protos import (
    BalanceRefProto,
    CheckoutIntentProto,
    CheckoutReqProto,
    CouponSpecProto,
    CustomerRefProto,
    CustomerSpecProto,
    InvoiceSpecProto,
    PaymentIntentReqProto,
    PaymentMethodRefProto,
    PaymentMethodSpecProto,
    PaymentRefProto,
    PayoutReqProto,
    PriceRefProto,
    PriceSpecProto,
    ProductRefProto,
    ProductSpecProto,
    PromotionSpecProto,
    RefundReqProto,
    ReportReqProto,
    SplitSpecProto,
    SubscriptionSpecProto,
    TransferReqProto,
    WebhookEventProto,
)

ALL_API_STRATEGIES: Tuple[Type[ABC], ...] = (
    IProductsPrices,
    IHostedCheckout,
    IOnlinePayments,
    ISubscriptions,
    IInvoicing,
    IMarketplace,
    IRisk,
    IRefunds,
    ICustomers,
    IPaymentMethods,
    IPayouts,
    IBalanceTransfers,
    IReports,
    IWebhooks,
    IPromotions,
)

__all__ = [
    "ALL_API_STRATEGIES",
    "ALL_CAPABILITIES",
    "CAPABILITY_TO_TIGRBL",
    "Capability",
    "Operation",
    "capabilities_to_tigrbl",
    "IBalanceTransfers",
    "IBillingProvider",
    "ICustomers",
    "IHostedCheckout",
    "IInvoicing",
    "IMarketplace",
    "IOnlinePayments",
    "IPaymentMethods",
    "IPayouts",
    "IPromotions",
    "IProductsPrices",
    "IRefunds",
    "IReports",
    "IRisk",
    "ISubscriptions",
    "IWebhooks",
    "BalanceRefProto",
    "CheckoutIntentProto",
    "CheckoutReqProto",
    "CouponSpecProto",
    "CustomerRefProto",
    "CustomerSpecProto",
    "InvoiceSpecProto",
    "PaymentIntentReqProto",
    "PaymentMethodRefProto",
    "PaymentMethodSpecProto",
    "PaymentRefProto",
    "PayoutReqProto",
    "PriceRefProto",
    "PriceSpecProto",
    "ProductRefProto",
    "ProductSpecProto",
    "PromotionSpecProto",
    "RefundReqProto",
    "ReportReqProto",
    "SplitSpecProto",
    "SubscriptionSpecProto",
    "TransferReqProto",
    "WebhookEventProto",
]
