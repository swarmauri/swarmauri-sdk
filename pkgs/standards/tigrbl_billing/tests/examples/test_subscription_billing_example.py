import pytest
from fastapi.routing import APIRoute

from tigrbl_billing.examples.subscription.subscription_billing_app import (
    build_subscription_billing_app,
    run_subscription_billing_flow,
)


@pytest.mark.asyncio
@pytest.mark.example
async def test_build_subscription_billing_app_registers_subscription_routes():
    app = build_subscription_billing_app(async_mode=True)
    registered_paths = {
        route.path for route in app.routes if isinstance(route, APIRoute)
    }

    expected = {
        "/product",
        "/price",
        "/feature",
        "/price_feature_entitlement",
        "/customer",
        "/subscription",
        "/subscription_item",
        "/usage_event",
        "/payment_intent",
        "/refund",
    }

    assert expected.issubset(registered_paths)


@pytest.mark.asyncio
@pytest.mark.example
async def test_run_subscription_billing_flow_configures_tiers_and_entitlements():
    app = build_subscription_billing_app(async_mode=True)
    result = await run_subscription_billing_flow(app)

    prices = result["prices"]

    assert set(prices.keys()) == {"free", "basic", "premium"}
    assert prices["free"]["price"]["unit_amount"] == 0
    assert prices["basic"]["price"]["metadata"]["tier"] == "basic"
    assert (
        prices["premium"]["entitlements"]["workspace_seats"]["limit_per_period"] == 20
    )
    assert all(
        entitlement["period"] == "month"
        for tier in prices.values()
        for entitlement in tier["entitlements"].values()
    )


@pytest.mark.asyncio
@pytest.mark.example
async def test_run_subscription_billing_flow_tracks_usage_and_refund():
    app = build_subscription_billing_app(async_mode=True)
    result = await run_subscription_billing_flow(app)

    usage = result["usage"]
    assert usage["total_quantity"] == 2500
    assert {event["idempotency_key"] for event in usage["events"]} == {
        "usage_basic_month_start",
        "usage_basic_mid_month",
    }

    payment_intent = result["payment_intent"]
    refund = result["refund"]
    assert refund["payment_intent_id"] == payment_intent["id"]
    assert refund["amount"] == 1500
    assert payment_intent["amount"] == result["prices"]["basic"]["price"]["unit_amount"]
