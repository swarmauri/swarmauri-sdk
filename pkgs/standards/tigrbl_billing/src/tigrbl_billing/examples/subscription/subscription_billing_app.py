"""Example application demonstrating tiered subscription billing."""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List

import httpx

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem

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


def build_subscription_billing_app(async_mode: bool = True) -> TigrblApp:
    """Create an application preloaded with subscription billing tables."""

    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models(
        [
            Product,
            Price,
            Feature,
            PriceFeatureEntitlement,
            Customer,
            Subscription,
            SubscriptionItem,
            UsageEvent,
            PaymentIntent,
            Refund,
        ]
    )
    return app


async def _create_feature_records(client: httpx.AsyncClient) -> Dict[str, str]:
    feature_payloads = [
        {
            "key": "workspace_seats",
            "name": "Workspace Seats",
            "description": "Number of users that can collaborate in the workspace.",
            "metering": "none",
            "unit_label": "seat",
            "metadata": {"category": "collaboration"},
        },
        {
            "key": "analytics_events",
            "name": "Analytics Events",
            "description": "Metered events processed for analytics dashboards.",
            "metering": "event",
            "unit_label": "event",
            "metadata": {"category": "usage"},
        },
    ]

    feature_ids: Dict[str, str] = {}
    for payload in feature_payloads:
        response = await client.post("/feature", json=payload)
        feature_ids[payload["key"]] = response.json()["data"]["id"]
    return feature_ids


async def _create_price_and_entitlements(
    client: httpx.AsyncClient, product_id: str, feature_ids: Dict[str, str]
) -> Dict[str, Dict[str, Any]]:
    tier_definitions = [
        {
            "metadata": {"tier": "free"},
            "nickname": "Free",
            "stripe_price_id": "price_subscription_free",
            "unit_amount": 0,
            "usage_type": "licensed",
            "entitlements": {
                "workspace_seats": {"limit": 1, "overage": None},
                "analytics_events": {"limit": 1000, "overage": None},
            },
        },
        {
            "metadata": {"tier": "basic"},
            "nickname": "Basic",
            "stripe_price_id": "price_subscription_basic",
            "unit_amount": 9900,
            "usage_type": "metered",
            "entitlements": {
                "workspace_seats": {"limit": 5, "overage": 1500},
                "analytics_events": {"limit": 10000, "overage": 25},
            },
        },
        {
            "metadata": {"tier": "premium"},
            "nickname": "Premium",
            "stripe_price_id": "price_subscription_premium",
            "unit_amount": 19900,
            "usage_type": "metered",
            "entitlements": {
                "workspace_seats": {"limit": 20, "overage": 1000},
                "analytics_events": {"limit": 50000, "overage": 15},
            },
        },
    ]

    prices: Dict[str, Dict[str, Any]] = {}
    for tier in tier_definitions:
        price_payload = {
            "stripe_price_id": tier["stripe_price_id"],
            "product_id": product_id,
            "currency": "usd",
            "billing_scheme": "flat",
            "unit_amount": tier["unit_amount"],
            "usage_type": tier["usage_type"],
            "recurring_interval": "month",
            "recurring_count": 1,
            "nickname": tier["nickname"],
            "metadata": tier["metadata"],
        }
        price_response = await client.post("/price", json=price_payload)
        price_id = price_response.json()["data"]["id"]
        price_record = (await client.get(f"/price/{price_id}")).json()

        entitlements: Dict[str, Dict[str, Any]] = {}
        for feature_key, entitlement in tier["entitlements"].items():
            entitlement_payload = {
                "price_id": price_id,
                "feature_id": feature_ids[feature_key],
                "limit_per_period": entitlement["limit"],
                "period": "month",
                "metering_window": "calendar",
            }
            if entitlement["overage"] is not None:
                entitlement_payload["overage_unit_amount"] = entitlement["overage"]

            entitlement_response = await client.post(
                "/price_feature_entitlement", json=entitlement_payload
            )
            entitlement_id = entitlement_response.json()["data"]["id"]
            entitlement_record = (
                await client.get(f"/price_feature_entitlement/{entitlement_id}")
            ).json()
            entitlements[feature_key] = {
                "limit_per_period": entitlement_record["limit_per_period"],
                "metering_window": entitlement_record["metering_window"],
                "period": entitlement_record["period"],
                "overage_unit_amount": entitlement_record.get("overage_unit_amount"),
            }

        prices[tier["metadata"]["tier"]] = {
            "price": price_record,
            "entitlements": entitlements,
        }
    return prices


async def run_subscription_billing_flow(
    app: TigrblApp | None = None,
) -> Dict[str, Any]:
    """Execute a subscription workflow with tiered entitlements and usage."""

    app = app or build_subscription_billing_app(async_mode=True)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://subscription-billing.test"
    ) as client:
        product_payload = {
            "stripe_product_id": "prod_subscription_suite",
            "name": "Subscription Suite",
            "description": "Tiered subscriptions with collaboration analytics.",
            "metadata": {"category": "saas"},
        }
        product_response = await client.post("/product", json=product_payload)
        product_id = product_response.json()["data"]["id"]
        product_record = (await client.get(f"/product/{product_id}")).json()

        feature_ids = await _create_feature_records(client)
        prices = await _create_price_and_entitlements(client, product_id, feature_ids)

        customer_payload = {
            "stripe_customer_id": "cus_subscription_owner",
            "email": "subscriber@example.com",
            "name": "Subscription Owner",
            "metadata": {"segment": "growth"},
        }
        customer_response = await client.post("/customer", json=customer_payload)
        customer_id = customer_response.json()["data"]["id"]
        customer_record = (await client.get(f"/customer/{customer_id}")).json()

        now = dt.datetime.now(tz=dt.timezone.utc)
        subscription_payload = {
            "stripe_subscription_id": "sub_basic_active",
            "customer_id": customer_id,
            "status": "active",
            "start_date": now.isoformat(),
            "cancel_at_period_end": False,
            "current_period_start": now.isoformat(),
            "current_period_end": (now + dt.timedelta(days=30)).isoformat(),
            "trial_end": (now + dt.timedelta(days=14)).isoformat(),
            "collection_method": "charge_automatically",
            "days_until_due": 0,
            "metadata": {"tier": "basic"},
        }
        subscription_response = await client.post(
            "/subscription", json=subscription_payload
        )
        subscription_id = subscription_response.json()["data"]["id"]
        subscription_record = (
            await client.get(f"/subscription/{subscription_id}")
        ).json()

        basic_price_id = prices["basic"]["price"]["id"]
        subscription_item_payload = {
            "subscription_id": subscription_id,
            "price_id": basic_price_id,
            "quantity": 1,
            "metadata": {"seats": 3},
        }
        subscription_item_response = await client.post(
            "/subscription_item", json=subscription_item_payload
        )
        subscription_item_id = subscription_item_response.json()["data"]["id"]
        subscription_item_record = (
            await client.get(f"/subscription_item/{subscription_item_id}")
        ).json()

        usage_events: List[Dict[str, Any]] = []
        usage_payloads = [
            {
                "subscription_item_id": subscription_item_id,
                "feature_id": feature_ids["analytics_events"],
                "quantity": 2000,
                "event_ts": now.isoformat(),
                "idempotency_key": "usage_basic_month_start",
                "source": "api",
                "metadata": {"description": "Initial migration"},
            },
            {
                "subscription_item_id": subscription_item_id,
                "feature_id": feature_ids["analytics_events"],
                "quantity": 500,
                "event_ts": (now + dt.timedelta(days=7)).isoformat(),
                "idempotency_key": "usage_basic_mid_month",
                "source": "api",
                "metadata": {"description": "Weekly usage"},
            },
        ]
        for payload in usage_payloads:
            usage_response = await client.post("/usage_event", json=payload)
            usage_id = usage_response.json()["data"]["id"]
            usage_record = (await client.get(f"/usage_event/{usage_id}")).json()
            usage_events.append(
                {
                    "quantity": usage_record["quantity"],
                    "feature_key": "analytics_events",
                    "source": usage_record["source"],
                    "idempotency_key": usage_record["idempotency_key"],
                }
            )

        payment_intent_payload = {
            "stripe_payment_intent_id": "pi_basic_subscription",
            "customer_id": customer_id,
            "currency": "usd",
            "amount": prices["basic"]["price"]["unit_amount"],
            "status": "succeeded",
            "capture_method": "automatic",
            "payment_method_types": ["card"],
            "metadata": {"subscription_id": subscription_id},
        }
        payment_intent_response = await client.post(
            "/payment_intent", json=payment_intent_payload
        )
        payment_intent_id = payment_intent_response.json()["data"]["id"]
        payment_intent_record = (
            await client.get(f"/payment_intent/{payment_intent_id}")
        ).json()

        refund_payload = {
            "stripe_refund_id": "re_basic_adjustment",
            "payment_intent_id": payment_intent_id,
            "amount": 1500,
            "status": "succeeded",
            "reason": "customer_requested",
            "metadata": {"description": "Seat downgrade credit"},
        }
        refund_response = await client.post("/refund", json=refund_payload)
        refund_id = refund_response.json()["data"]["id"]
        refund_record = (await client.get(f"/refund/{refund_id}")).json()

        usage_summary = {
            "events": usage_events,
            "total_quantity": sum(event["quantity"] for event in usage_events),
        }

        return {
            "product": product_record,
            "customer": customer_record,
            "prices": prices,
            "subscription": subscription_record,
            "subscription_item": subscription_item_record,
            "usage": usage_summary,
            "payment_intent": payment_intent_record,
            "refund": refund_record,
        }
