import pytest

from tigrbl_billing.api import api_basic_subscriptions


@pytest.mark.asyncio
async def test_subscription_start_and_cancel(uvicorn_client):
    async with uvicorn_client(api_basic_subscriptions.app) as client:
        start = await client.post(
            "/subscription/start",
            json={
                "customer_id": "cust-1",
                "items": [{"price_id": "price-monthly", "quantity": 1}],
                "collection_method": "charge_automatically",
            },
        )
        assert start.status_code == 200
        subscription_id = start.json()["data"]["id"]

        cancel = await client.post(
            "/subscription/cancel",
            json={"subscription_id": subscription_id, "cancel_at_period_end": False},
        )
        assert cancel.status_code == 200

        listing = await client.get("/subscription")
        sub = listing.json()["items"][0]
        assert sub["status"] == "CANCELED"
        assert sub["cancel_at_period_end"] is False


@pytest.mark.asyncio
async def test_subscription_resume_sets_active_state(uvicorn_client):
    async with uvicorn_client(api_basic_subscriptions.app) as client:
        start = await client.post(
            "/subscription/start",
            json={"customer_id": "cust-2", "items": []},
        )
        subscription_id = start.json()["data"]["id"]

        pause = await client.post(
            "/subscription/pause", json={"subscription_id": subscription_id}
        )
        assert pause.status_code == 200

        resume = await client.post(
            "/subscription/resume", json={"subscription_id": subscription_id}
        )
        assert resume.status_code == 200

        read = await client.get(f"/subscription/{subscription_id}")
        record = read.json()
        assert record["status"] == "ACTIVE"
        assert record["cancel_at_period_end"] is False
