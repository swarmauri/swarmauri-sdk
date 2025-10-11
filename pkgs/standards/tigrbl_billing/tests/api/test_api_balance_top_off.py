import pytest

from tigrbl_billing.api import api_balance_top_off


@pytest.mark.asyncio
async def test_request_top_off_creates_customer_balance_entry(uvicorn_client):
    async with uvicorn_client(api_balance_top_off.app) as client:
        response = await client.post(
            "/customer_balance/request_top_off",
            json={
                "balance_id": "bal-1",
                "amount": 2500,
                "currency": "usd",
                "trigger": "manual",
                "method": "payment_intent",
            },
        )
        data = response.json()
        assert response.status_code == 200
        assert data["status"] == "ok"

        listing = await client.get("/customer_balance")
        balances = listing.json()["items"]
        assert balances[0]["amount"] == 2500
        assert balances[0]["status"] == "INITIATED"


@pytest.mark.asyncio
async def test_apply_top_off_updates_status_and_failure_reason(uvicorn_client):
    async with uvicorn_client(api_balance_top_off.app) as client:
        created = await client.post(
            "/balance_top_off",
            json={"status": "INITIATED", "metadata": {"source": "charge"}},
        )
        top_off_id = created.json()["data"]["id"]

        update = await client.post(
            "/balance_top_off/apply_top_off",
            json={
                "top_off_id": top_off_id,
                "status": "FAILED",
                "failure_reason": "card_declined",
            },
        )
        assert update.status_code == 200

        listing = await client.get("/balance_top_off")
        record = listing.json()["items"][0]
        assert record["status"] == "FAILED"
        assert record["failure_reason"] == "card_declined"


@pytest.mark.asyncio
async def test_check_and_top_off_returns_intent_signal(uvicorn_client):
    async with uvicorn_client(api_balance_top_off.app) as client:
        response = await client.post(
            "/customer_balance/check_and_top_off",
            json={"balance_id": "bal-2"},
        )
        body = response.json()
        assert response.status_code == 200
        assert body == {"balance_id": "bal-2", "top_off_created": False}
