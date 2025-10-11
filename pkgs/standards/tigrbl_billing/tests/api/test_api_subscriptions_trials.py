import pytest

from tigrbl_billing.api import api_subscriptions_trials


@pytest.mark.asyncio
async def test_trial_start_and_end_updates_status(uvicorn_client):
    async with uvicorn_client(api_subscriptions_trials.app) as client:
        base = await client.post(
            "/subscription",
            json={"customer_id": "cust-trial", "status": "ACTIVE", "items": []},
        )
        subscription_id = base.json()["data"]["id"]

        start = await client.post(
            "/subscription/trial_start",
            json={"subscription_id": subscription_id, "trial_end": "2024-01-01"},
        )
        assert start.status_code == 200

        end = await client.post(
            "/subscription/trial_end", json={"subscription_id": subscription_id}
        )
        assert end.status_code == 200

        record = (await client.get(f"/subscription/{subscription_id}")).json()
        assert record["status"] == "ACTIVE"
        assert record["trial_end"] is None


@pytest.mark.asyncio
async def test_proration_preview_returns_payload(uvicorn_client):
    async with uvicorn_client(api_subscriptions_trials.app) as client:
        preview = await client.post(
            "/subscription/proration_preview",
            json={
                "subscription_id": "sub-preview",
                "proposed_items": [{"price_id": "price-new", "quantity": 2}],
            },
        )
        body = preview.json()
        assert body["subscription_id"] == "sub-preview"
        assert body["preview"][0]["price_id"] == "price-new"
