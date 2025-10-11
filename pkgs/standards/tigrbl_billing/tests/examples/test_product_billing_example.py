import pytest
from fastapi.routing import APIRoute

from tigrbl_billing.examples.product_billing_app import (
    build_product_billing_app,
    run_product_billing_flow,
)


@pytest.mark.asyncio
@pytest.mark.example
async def test_build_product_billing_app_registers_routes():
    app = build_product_billing_app(async_mode=True)
    registered_paths = {
        route.path for route in app.routes if isinstance(route, APIRoute)
    }

    expected = {
        "/product",
        "/price",
        "/customer",
        "/checkout_session",
        "/payment_intent",
        "/refund",
    }

    for path in expected:
        assert path in registered_paths


@pytest.mark.asyncio
@pytest.mark.example
async def test_run_product_billing_flow_creates_product_and_price():
    app = build_product_billing_app(async_mode=True)
    result = await run_product_billing_flow(app)

    assert result["product"]["name"] == "Simple Suite"
    assert result["price"]["product_id"] == result["product"]["id"]
    assert result["price"]["unit_amount"] == 4999
    assert (
        result["checkout"]["line_items"]["items"][0]["price_id"]
        == result["price"]["id"]
    )


@pytest.mark.asyncio
@pytest.mark.example
async def test_run_product_billing_flow_handles_partial_refund():
    app = build_product_billing_app(async_mode=True)
    result = await run_product_billing_flow(app)

    assert result["refund"]["payment_intent_id"] == result["payment_intent"]["id"]
    assert result["refund"]["amount"] == 1999
    assert result["payment_intent"]["amount"] == 4999
    assert result["refund"]["amount"] < result["payment_intent"]["amount"]
    assert result["refund"]["status"] == "succeeded"
