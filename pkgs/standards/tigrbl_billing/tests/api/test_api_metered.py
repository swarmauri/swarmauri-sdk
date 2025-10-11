import pytest

from tigrbl_billing.api import api_metered


@pytest.mark.asyncio
async def test_record_usage_event(uvicorn_client):
    async with uvicorn_client(api_metered.app) as client:
        create = await client.post(
            "/usage_event",
            json={
                "usage_event_id": "evt-metered",
                "customer_id": "cust-meter",
                "feature_key": "api_calls",
                "quantity": 10,
                "currency": "usd",
            },
        )
        assert create.status_code == 200

        listing = await client.get("/usage_event")
        events = listing.json()["items"]
        assert events[0]["usage_event_id"] == "evt-metered"
        assert events[0]["quantity"] == 10
