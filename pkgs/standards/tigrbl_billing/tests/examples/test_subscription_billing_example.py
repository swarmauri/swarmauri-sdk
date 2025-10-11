import datetime as dt

import pytest
from fastapi.routing import APIRoute

from tigrbl_billing.examples.subscription_billing_app import (
    build_subscription_billing_app,
    run_subscription_billing_flow,
)


@pytest.mark.asyncio
@pytest.mark.example
async def test_build_subscription_billing_app_registers_core_routes() -> None:
    app = build_subscription_billing_app(async_mode=True)
    registered_paths = {
        route.path for route in app.routes if isinstance(route, APIRoute)
    }

    expected_paths = {
        "/product",
        "/feature",
        "/price",
        "/price_feature_entitlement",
        "/customer",
        "/subscription",
        "/subscription_item",
        "/seat_allocation",
        "/usage_event",
        "/payment_intent",
        "/refund",
    }

    for path in expected_paths:
        assert path in registered_paths


@pytest.mark.asyncio
@pytest.mark.example
async def test_run_subscription_billing_flow_creates_all_tiers() -> None:
    app = build_subscription_billing_app(async_mode=True)
    result = await run_subscription_billing_flow(app)

    tiers = result["prices"]
    assert set(tiers) == {"free", "basic", "pro", "premium"}
    assert tiers["free"]["unit_amount"] == 0
    assert tiers["basic"]["unit_amount"] == 2900
    assert tiers["pro"]["metadata"]["usage_limits"]["api_requests"] == 50000
    assert tiers["premium"]["metadata"]["supports_multi_seat"] is True


@pytest.mark.asyncio
@pytest.mark.example
async def test_run_subscription_billing_flow_sets_trial_period() -> None:
    app = build_subscription_billing_app(async_mode=True)
    result = await run_subscription_billing_flow(app)

    subscription = result["subscription"]
    start_date = dt.datetime.fromisoformat(subscription["start_date"])
    trial_end = dt.datetime.fromisoformat(subscription["trial_end"])

    assert subscription["status"] == "trialing"
    assert trial_end - start_date == dt.timedelta(days=14)


@pytest.mark.asyncio
@pytest.mark.example
async def test_run_subscription_billing_flow_assigns_seats_and_usage() -> None:
    app = build_subscription_billing_app(async_mode=True)
    result = await run_subscription_billing_flow(app)

    seat_allocations = result["seat_allocations"]
    assert len(seat_allocations) == 3
    subject_refs = {seat["subject_ref"] for seat in seat_allocations}
    assert subject_refs == {"user:founder", "user:ops-lead", "user:data-scientist"}

    subscription_item = result["subscription_item"]
    assert subscription_item["quantity"] == 25
    assert all(
        seat["subscription_item_id"] == subscription_item["id"]
        for seat in seat_allocations
    )

    usage_event = result["usage_event"]
    assert usage_event["quantity"] == 4200
    assert usage_event["source"] == "api"


@pytest.mark.asyncio
@pytest.mark.example
async def test_run_subscription_billing_flow_supports_refunds() -> None:
    app = build_subscription_billing_app(async_mode=True)
    result = await run_subscription_billing_flow(app)

    refund = result["refund"]
    payment_intent = result["payment_intent"]

    assert refund["payment_intent_id"] == payment_intent["id"]
    assert refund["amount"] == 12900 // 5
    assert payment_intent["amount"] == 12900
    assert refund["status"] == "succeeded"
