"""Subscription billing example showcasing tiered plans with usage limits."""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict

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
from tigrbl_billing.tables.seat_allocation import SeatAllocation
from tigrbl_billing.tables.subscription import Subscription
from tigrbl_billing.tables.subscription_item import SubscriptionItem
from tigrbl_billing.tables.usage_event import UsageEvent


def build_subscription_billing_app(async_mode: bool = True) -> TigrblApp:
    """Instantiate an application preloaded with subscription billing tables."""

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
            SeatAllocation,
            UsageEvent,
            PaymentIntent,
            Refund,
        ]
    )
    return app


async def run_subscription_billing_flow(app: TigrblApp | None = None) -> Dict[str, Any]:
    """Execute a subscription onboarding flow with tiered pricing."""

    app = app or build_subscription_billing_app(async_mode=True)

    now = dt.datetime.now(dt.timezone.utc)
    trial_end = now + dt.timedelta(days=14)
    period_end = now + dt.timedelta(days=30)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://subscription-billing.test"
    ) as client:
        product_payload = {
            "stripe_product_id": "prod_atlas_workspace",
            "name": "Atlas Workspace",
            "description": "Collaboration suite with analytics and automation",
            "metadata": {"department": "product"},
        }
        product_response = await client.post("/product", json=product_payload)
        product_id = product_response.json()["data"]["id"]

        feature_payloads = [
            {
                "key": "api_requests",
                "name": "API Requests",
                "description": "Metered calls against the public API",
                "metering": "event",
                "unit_label": "calls",
                "metadata": {"unit": "request"},
            },
            {
                "key": "automation_runs",
                "name": "Automation Runs",
                "description": "Workflow executions triggered by schedules",
                "metering": "event",
                "unit_label": "runs",
                "metadata": {"unit": "run"},
            },
            {
                "key": "seats",
                "name": "Seats",
                "description": "Billable collaborators able to sign in",
                "metering": "none",
                "unit_label": "seats",
                "metadata": {"note": "managed via subscription quantity"},
            },
        ]

        feature_ids: Dict[str, str] = {}
        for payload in feature_payloads:
            feature_response = await client.post("/feature", json=payload)
            feature_ids[payload["key"]] = feature_response.json()["data"]["id"]

        price_definitions = {
            "free": {
                "stripe_price_id": "price_atlas_free",
                "currency": "usd",
                "billing_scheme": "flat",
                "unit_amount": 0,
                "usage_type": "licensed",
                "recurring_interval": "month",
                "recurring_count": 1,
                "nickname": "Free",
                "metadata": {
                    "tier": "free",
                    "monthly_seat_limit": 1,
                    "usage_limits": {"api_requests": 1000, "automation_runs": 50},
                },
            },
            "basic": {
                "stripe_price_id": "price_atlas_basic",
                "currency": "usd",
                "billing_scheme": "flat",
                "unit_amount": 2900,
                "usage_type": "licensed",
                "recurring_interval": "month",
                "recurring_count": 1,
                "nickname": "Basic",
                "metadata": {
                    "tier": "basic",
                    "monthly_seat_limit": 5,
                    "usage_limits": {"api_requests": 10000, "automation_runs": 500},
                },
            },
            "pro": {
                "stripe_price_id": "price_atlas_pro",
                "currency": "usd",
                "billing_scheme": "flat",
                "unit_amount": 5900,
                "usage_type": "licensed",
                "recurring_interval": "month",
                "recurring_count": 1,
                "nickname": "Pro",
                "metadata": {
                    "tier": "pro",
                    "monthly_seat_limit": 15,
                    "usage_limits": {"api_requests": 50000, "automation_runs": 2500},
                },
            },
            "premium": {
                "stripe_price_id": "price_atlas_premium",
                "currency": "usd",
                "billing_scheme": "flat",
                "unit_amount": 12900,
                "usage_type": "licensed",
                "recurring_interval": "month",
                "recurring_count": 1,
                "nickname": "Premium",
                "metadata": {
                    "tier": "premium",
                    "supports_multi_seat": True,
                    "monthly_seat_limit": 50,
                    "usage_limits": {"api_requests": 200000, "automation_runs": 10000},
                },
            },
        }

        price_ids: Dict[str, str] = {}
        for tier, payload in price_definitions.items():
            payload_with_product = dict(payload, product_id=product_id)
            price_response = await client.post("/price", json=payload_with_product)
            price_ids[tier] = price_response.json()["data"]["id"]

        entitlement_payloads = [
            {
                "price_id": price_ids["free"],
                "feature_id": feature_ids["api_requests"],
                "limit_per_period": 1000,
                "overage_unit_amount": 0,
                "period": "month",
                "metering_window": "calendar",
            },
            {
                "price_id": price_ids["free"],
                "feature_id": feature_ids["automation_runs"],
                "limit_per_period": 50,
                "overage_unit_amount": 0,
                "period": "month",
                "metering_window": "calendar",
            },
            {
                "price_id": price_ids["basic"],
                "feature_id": feature_ids["api_requests"],
                "limit_per_period": 10000,
                "overage_unit_amount": 15,
                "period": "month",
                "metering_window": "calendar",
            },
            {
                "price_id": price_ids["pro"],
                "feature_id": feature_ids["api_requests"],
                "limit_per_period": 50000,
                "overage_unit_amount": 10,
                "period": "month",
                "metering_window": "calendar",
            },
            {
                "price_id": price_ids["premium"],
                "feature_id": feature_ids["api_requests"],
                "limit_per_period": 200000,
                "overage_unit_amount": 5,
                "period": "month",
                "metering_window": "calendar",
            },
            {
                "price_id": price_ids["premium"],
                "feature_id": feature_ids["seats"],
                "limit_per_period": 50,
                "overage_unit_amount": 1500,
                "period": "month",
                "metering_window": "calendar",
            },
        ]

        entitlement_records = []
        for payload in entitlement_payloads:
            entitlement_response = await client.post(
                "/price_feature_entitlement", json=payload
            )
            entitlement_id = entitlement_response.json()["data"]["id"]
            entitlement_record = await client.get(
                f"/price_feature_entitlement/{entitlement_id}"
            )
            entitlement_records.append(entitlement_record.json())

        customer_payload = {
            "stripe_customer_id": "cus_atlas_labs",
            "email": "billing@atlaslabs.example",
            "name": "Atlas Labs Inc.",
            "default_payment_method_ref": "pm_visa_corporate",
            "metadata": {"account_tier": "premium"},
        }
        customer_response = await client.post("/customer", json=customer_payload)
        customer_id = customer_response.json()["data"]["id"]

        subscription_payload = {
            "stripe_subscription_id": "sub_atlas_premium",
            "customer_id": customer_id,
            "status": "trialing",
            "start_date": now.isoformat(),
            "cancel_at_period_end": False,
            "current_period_start": now.isoformat(),
            "current_period_end": period_end.isoformat(),
            "trial_end": trial_end.isoformat(),
            "collection_method": "charge_automatically",
            "days_until_due": None,
            "metadata": {"sales_owner": "enterprise-team"},
        }
        subscription_response = await client.post(
            "/subscription", json=subscription_payload
        )
        subscription_id = subscription_response.json()["data"]["id"]

        subscription_item_payload = {
            "subscription_id": subscription_id,
            "price_id": price_ids["premium"],
            "stripe_subscription_item_id": "si_atlas_premium_core",
            "quantity": 25,
            "metadata": {"seats_purchased": 25},
        }
        subscription_item_response = await client.post(
            "/subscription_item", json=subscription_item_payload
        )
        subscription_item_id = subscription_item_response.json()["data"]["id"]

        seat_subjects = [
            ("user:founder", "owner"),
            ("user:ops-lead", "administrator"),
            ("user:data-scientist", "analyst"),
        ]
        seat_records = []
        for subject_ref, role in seat_subjects:
            seat_payload = {
                "subscription_item_id": subscription_item_id,
                "subject_ref": subject_ref,
                "role": role,
                "state": "active",
                "assigned_at": now.isoformat(),
                "released_at": None,
            }
            seat_response = await client.post("/seat_allocation", json=seat_payload)
            seat_id = seat_response.json()["data"]["id"]
            seat_record = await client.get(f"/seat_allocation/{seat_id}")
            seat_records.append(seat_record.json())

        usage_payload = {
            "subscription_item_id": subscription_item_id,
            "feature_id": feature_ids["api_requests"],
            "quantity": 4200,
            "event_ts": now.isoformat(),
            "idempotency_key": "usage_atlas_premium_m1",
            "source": "api",
            "metadata": {"batch": "march-usage", "reported_by": "usage-daemon"},
        }
        usage_response = await client.post("/usage_event", json=usage_payload)
        usage_event_id = usage_response.json()["data"]["id"]

        payment_intent_payload = {
            "stripe_payment_intent_id": "pi_atlas_initial_invoice",
            "customer_id": customer_id,
            "currency": "usd",
            "amount": 12900,
            "status": "succeeded",
            "capture_method": "automatic",
            "payment_method_types": ["card"],
            "metadata": {
                "subscription_id": subscription_id,
                "invoice_number": "ATLS-0001",
            },
        }
        payment_intent_response = await client.post(
            "/payment_intent", json=payment_intent_payload
        )
        payment_intent_id = payment_intent_response.json()["data"]["id"]

        refund_payload = {
            "stripe_refund_id": "re_atlas_seat_adjustment",
            "payment_intent_id": payment_intent_id,
            "amount": 12900 // 5,
            "status": "succeeded",
            "reason": "seat_downsize_credit",
            "metadata": {"requested_by": "ops-lead"},
        }
        refund_response = await client.post("/refund", json=refund_payload)
        refund_id = refund_response.json()["data"]["id"]

        product_record = (await client.get(f"/product/{product_id}")).json()
        feature_records = {
            key: (await client.get(f"/feature/{feature_id}")).json()
            for key, feature_id in feature_ids.items()
        }
        price_records = {
            tier: (await client.get(f"/price/{price_id}")).json()
            for tier, price_id in price_ids.items()
        }
        subscription_record = (
            await client.get(f"/subscription/{subscription_id}")
        ).json()
        subscription_item_record = (
            await client.get(f"/subscription_item/{subscription_item_id}")
        ).json()
        usage_event_record = (await client.get(f"/usage_event/{usage_event_id}")).json()
        payment_intent_record = (
            await client.get(f"/payment_intent/{payment_intent_id}")
        ).json()
        refund_record = (await client.get(f"/refund/{refund_id}")).json()

        return {
            "product": product_record,
            "features": feature_records,
            "prices": price_records,
            "entitlements": entitlement_records,
            "subscription": subscription_record,
            "subscription_item": subscription_item_record,
            "seat_allocations": seat_records,
            "usage_event": usage_event_record,
            "payment_intent": payment_intent_record,
            "refund": refund_record,
        }
