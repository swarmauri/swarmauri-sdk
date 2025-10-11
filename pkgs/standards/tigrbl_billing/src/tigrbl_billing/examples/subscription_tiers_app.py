"""Example app showcasing subscription tiers with usage limits and refunds."""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict

import httpx

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing import ops as billing_ops
from tigrbl_billing.tables.customer import Customer
from tigrbl_billing.tables.feature import Feature
from tigrbl_billing.tables.payment_intent import PaymentIntent
from tigrbl_billing.tables.price import Price
from tigrbl_billing.tables.price_feature_entitlement import PriceFeatureEntitlement
from tigrbl_billing.tables.product import Product
from tigrbl_billing.tables.refund import Refund
from tigrbl_billing.tables.subscription import Subscription
from tigrbl_billing.tables.subscription_item import SubscriptionItem
from tigrbl_billing.tables.usage_event import UsageEvent
from tigrbl_billing.tables.usage_rollup import UsageRollup

_REQUIRED_OPS = (
    billing_ops.start_subscription,
    billing_ops.cancel_subscription,
    billing_ops.resume_subscription,
    billing_ops.pause_subscription,
    billing_ops.trial_start,
    billing_ops.trial_end,
    billing_ops.rollup_usage_periodic,
    billing_ops.sync_objects,
)


def build_subscription_tiers_app(async_mode: bool = True) -> TigrblApp:
    """Create a :class:`~tigrbl.TigrblApp` preloaded with subscription billing tables."""

    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models(
        [
            Product,
            Feature,
            Price,
            PriceFeatureEntitlement,
            Customer,
            Subscription,
            SubscriptionItem,
            UsageEvent,
            UsageRollup,
            PaymentIntent,
            Refund,
        ]
    )
    return app


async def run_subscription_tiers_flow(app: TigrblApp | None = None) -> Dict[str, Any]:
    """Provision subscription tiers, track usage, and handle a refund."""

    app = app or build_subscription_tiers_app(async_mode=True)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://subscription-billing.test"
    ) as client:
        feature_payloads = [
            {
                "key": "projects",
                "name": "Projects",
                "description": "Active project workspaces",
                "metering": "none",
                "unit_label": "projects",
                "metadata": {"category": "collaboration"},
            },
            {
                "key": "api_requests",
                "name": "API Requests",
                "description": "Metered API calls per month",
                "metering": "event",
                "unit_label": "requests",
                "metadata": {"category": "integration"},
            },
        ]

        features: Dict[str, Dict[str, Any]] = {}
        for payload in feature_payloads:
            response = await client.post("/feature", json=payload)
            features[payload["key"]] = response.json()["data"]

        product_payload = {
            "stripe_product_id": "prod_collaboration_hub",
            "name": "Collaboration Hub",
            "description": "Team work management platform",
            "metadata": {"segment": "b2b"},
        }
        product_response = await client.post("/product", json=product_payload)
        product = product_response.json()["data"]

        price_definitions = {
            "free": {
                "stripe_price_id": "price_collab_free",
                "currency": "usd",
                "billing_scheme": "flat",
                "unit_amount": 0,
                "recurring_interval": "month",
                "recurring_count": 1,
                "usage_type": "licensed",
                "nickname": "Free",
                "metadata": {"tier": "free"},
            },
            "basic": {
                "stripe_price_id": "price_collab_basic",
                "currency": "usd",
                "billing_scheme": "flat",
                "unit_amount": 2900,
                "recurring_interval": "month",
                "recurring_count": 1,
                "usage_type": "licensed",
                "nickname": "Basic",
                "metadata": {"tier": "basic"},
            },
            "premium": {
                "stripe_price_id": "price_collab_premium",
                "currency": "usd",
                "billing_scheme": "flat",
                "unit_amount": 7900,
                "recurring_interval": "month",
                "recurring_count": 1,
                "usage_type": "licensed",
                "nickname": "Premium",
                "metadata": {"tier": "premium"},
            },
        }

        prices: Dict[str, Dict[str, Any]] = {}
        for tier, price_payload in price_definitions.items():
            payload = {"product_id": product["id"], **price_payload}
            response = await client.post("/price", json=payload)
            prices[tier] = response.json()["data"]

        entitlement_matrix = {
            "free": {
                "projects": {
                    "limit_per_period": 1,
                    "period": "month",
                },
                "api_requests": {
                    "limit_per_period": 1000,
                    "period": "month",
                    "overage_unit_amount": 0,
                },
            },
            "basic": {
                "projects": {
                    "limit_per_period": 5,
                    "period": "month",
                },
                "api_requests": {
                    "limit_per_period": 5000,
                    "period": "month",
                    "overage_unit_amount": 25,
                },
            },
            "premium": {
                "projects": {
                    "limit_per_period": 20,
                    "period": "month",
                },
                "api_requests": {
                    "limit_per_period": 50000,
                    "period": "month",
                    "overage_unit_amount": 10,
                },
            },
        }

        entitlements: Dict[str, Dict[str, Any]] = {
            "free": {},
            "basic": {},
            "premium": {},
        }
        for tier, feature_limits in entitlement_matrix.items():
            for feature_key, limits in feature_limits.items():
                payload = {
                    "price_id": prices[tier]["id"],
                    "feature_id": features[feature_key]["id"],
                    "limit_per_period": limits.get("limit_per_period"),
                    "overage_unit_amount": limits.get("overage_unit_amount"),
                    "period": limits.get("period"),
                    "metering_window": "calendar",
                }
                response = await client.post("/price_feature_entitlement", json=payload)
                entitlements[tier][feature_key] = response.json()["data"]

        customer_payload = {
            "stripe_customer_id": "cus_collab_acme",
            "email": "billing@acme.io",
            "name": "Acme Collaboration Team",
            "metadata": {"account_tier": "basic"},
        }
        customer_response = await client.post("/customer", json=customer_payload)
        customer = customer_response.json()["data"]

        now = dt.datetime.now(dt.timezone.utc)
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + dt.timedelta(days=30)

        subscription_payload = {
            "stripe_subscription_id": "sub_collab_basic",
            "customer_id": customer["id"],
            "status": "active",
            "start_date": now.isoformat(),
            "cancel_at_period_end": False,
            "current_period_start": period_start.isoformat(),
            "current_period_end": period_end.isoformat(),
            "trial_end": (now + dt.timedelta(days=14)).isoformat(),
            "collection_method": "charge_automatically",
            "days_until_due": None,
            "metadata": {"plan": "basic", "tier": "basic"},
        }
        subscription_response = await client.post(
            "/subscription", json=subscription_payload
        )
        subscription = subscription_response.json()["data"]

        subscription_item_payload = {
            "subscription_id": subscription["id"],
            "price_id": prices["basic"]["id"],
            "stripe_subscription_item_id": "si_collab_basic",
            "quantity": 10,
            "metadata": {"tier": "basic"},
        }
        subscription_item_response = await client.post(
            "/subscription_item", json=subscription_item_payload
        )
        subscription_item = subscription_item_response.json()["data"]

        usage_event_payload = {
            "subscription_item_id": subscription_item["id"],
            "feature_id": features["api_requests"]["id"],
            "quantity": 3200,
            "event_ts": now.isoformat(),
            "idempotency_key": "usage_collab_basic_2024_04",
            "source": "api",
            "metadata": {"window": "2024-04"},
        }
        usage_event_response = await client.post(
            "/usage_event", json=usage_event_payload
        )
        usage_event = usage_event_response.json()["data"]

        usage_rollup_payload = {
            "subscription_item_id": subscription_item["id"],
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "quantity_sum": 3200,
            "last_event_ts": now.isoformat(),
        }
        usage_rollup_response = await client.post(
            "/usage_rollup", json=usage_rollup_payload
        )
        usage_rollup = usage_rollup_response.json()["data"]

        payment_intent_payload = {
            "stripe_payment_intent_id": "pi_collab_basic_apr",
            "customer_id": customer["id"],
            "currency": "usd",
            "amount": prices["basic"]["unit_amount"],
            "status": "succeeded",
            "capture_method": "automatic",
            "payment_method_types": ["card"],
            "metadata": {
                "subscription_id": subscription["id"],
                "billing_period_start": period_start.isoformat(),
            },
        }
        payment_intent_response = await client.post(
            "/payment_intent", json=payment_intent_payload
        )
        payment_intent = payment_intent_response.json()["data"]

        refund_payload = {
            "stripe_refund_id": "re_collab_basic_credit",
            "payment_intent_id": payment_intent["id"],
            "amount": 900,
            "status": "succeeded",
            "reason": "service_credit",
            "metadata": {"issued_by": "support"},
        }
        refund_response = await client.post("/refund", json=refund_payload)
        refund = refund_response.json()["data"]

        return {
            "product": product,
            "features": features,
            "prices": prices,
            "entitlements": entitlements,
            "customer": customer,
            "subscription": subscription,
            "subscription_item": subscription_item,
            "usage": {
                "event": usage_event,
                "rollup": usage_rollup,
            },
            "payment_intent": payment_intent,
            "refund": refund,
        }
