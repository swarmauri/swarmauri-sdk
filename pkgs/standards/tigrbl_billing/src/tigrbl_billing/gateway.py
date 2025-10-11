from typing import Dict
from tigrbl import TigrblApp

from .api import api_product_price as product_price
from .api import api_tiered as tiered
from .api import api_complex_tiers as complex_tiers
from .api import api_seats as seats
from .api import api_metered as metered
from .api import api_invoice_payment as invoice_payment
from .api import api_checkout as checkout
from .api import api_usage_based as usage_based
from .api import api_banded_pricing as banded_pricing
from .api import api_basic_subscriptions as basic_subscriptions
from .api import api_subscriptions_trials as subscriptions_trials
from .api import api_customer_to_customer as customer_to_customer
from .api import api_payment_splitting as payment_splitting
from .api import api_stripe_connected_accounts as stripe_connected_accounts
from .api import api_stripe_customer_accounts as stripe_customer_accounts


def build_all_apps(async_mode: bool = True) -> Dict[str, TigrblApp]:
    return {
        "product_price": product_price.build_app(async_mode),
        "tiered": tiered.build_app(async_mode),
        "complex_tiers": complex_tiers.build_app(async_mode),
        "seats": seats.build_app(async_mode),
        "metered": metered.build_app(async_mode),
        "invoice_payment": invoice_payment.build_app(async_mode),
        "checkout": checkout.build_app(async_mode),
        "usage_based": usage_based.build_app(async_mode),
        "banded_pricing": banded_pricing.build_app(async_mode),
        "basic_subscriptions": basic_subscriptions.build_app(async_mode),
        "subscriptions_trials": subscriptions_trials.build_app(async_mode),
        "customer_to_customer": customer_to_customer.build_app(async_mode),
        "payment_splitting": payment_splitting.build_app(async_mode),
        "stripe_connected_accounts": stripe_connected_accounts.build_app(async_mode),
        "stripe_customer_accounts": stripe_customer_accounts.build_app(async_mode),
    }
