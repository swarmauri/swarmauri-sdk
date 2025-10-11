import pytest
from fastapi.routing import APIRoute

from tigrbl_billing.examples.subscription_tiers_app import (
    build_subscription_tiers_app,
    run_subscription_tiers_flow,
)


@pytest.mark.asyncio
@pytest.mark.example
async def test_build_subscription_tiers_app_registers_routes():
    app = build_subscription_tiers_app(async_mode=True)
    registered_paths = {route.path for route in app.routes if isinstance(route, APIRoute)}

    expected_paths = {
        "/product",
        "/feature",
        "/price",
        "/price_feature_entitlement",
        "/customer",
        "/subscription",
        "/subscription_item",
        "/usage_event",
        "/usage_rollup",
        "/payment_intent",
        "/refund",
    }

    assert expected_paths.issubset(registered_paths)


@pytest.mark.asyncio
@pytest.mark.example
async def test_run_subscription_tiers_flow_sets_entitlements_per_tier():
    app = build_subscription_tiers_app(async_mode=True)
    result = await run_subscription_tiers_flow(app)

    assert result["entitlements"]["free"]["projects"]["limit_per_period"] == 1
    assert result["entitlements"]["basic"]["projects"]["limit_per_period"] == 5
    assert result["entitlements"]["premium"]["projects"]["limit_per_period"] == 20

    assert result["entitlements"]["basic"]["api_requests"]["limit_per_period"] == 5000
    assert result["entitlements"]["premium"]["api_requests"]["overage_unit_amount"] == 10


@pytest.mark.asyncio
@pytest.mark.example
async def test_run_subscription_tiers_flow_tracks_usage_activity():
    app = build_subscription_tiers_app(async_mode=True)
    result = await run_subscription_tiers_flow(app)

    usage_event = result["usage"]["event"]
    usage_rollup = result["usage"]["rollup"]

    assert usage_event["quantity"] == 3200
    assert usage_event["subscription_item_id"] == result["subscription_item"]["id"]
    assert usage_rollup["quantity_sum"] == 3200
    assert usage_rollup["subscription_item_id"] == result["subscription_item"]["id"]


@pytest.mark.asyncio
@pytest.mark.example
async def test_run_subscription_tiers_flow_records_refund_against_payment():
    app = build_subscription_tiers_app(async_mode=True)
    result = await run_subscription_tiers_flow(app)

    refund = result["refund"]
    payment_intent = result["payment_intent"]

    assert refund["payment_intent_id"] == payment_intent["id"]
    assert refund["amount"] < payment_intent["amount"]
    assert refund["status"] == "succeeded"
