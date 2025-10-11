import pytest

from tigrbl_billing.api import api_credit_usage


@pytest.mark.asyncio
async def test_charge_credits_records_usage_event(uvicorn_client):
    async with uvicorn_client(api_credit_usage.app) as client:
        response = await client.post(
            "/usage_event/charge_credits",
            json={
                "usage_event_id": "evt-1",
                "customer_id": "cust-credits",
                "feature_key": "storage",
                "quantity": 5,
                "currency": "usd",
                "metadata": {"note": "overage"},
            },
        )
        assert response.status_code == 200

        events = await client.get("/usage_event")
        items = events.json()["items"]
        assert items[0]["usage_event_id"] == "evt-1"
        assert items[0]["direction"] == "DEBIT"
        assert items[0]["quantity"] == 5
