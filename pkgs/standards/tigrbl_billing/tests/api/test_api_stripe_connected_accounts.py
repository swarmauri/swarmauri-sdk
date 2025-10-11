import pytest

from tigrbl_billing.api import api_stripe_connected_accounts


@pytest.mark.asyncio
async def test_create_connected_account_and_link(uvicorn_client):
    async with uvicorn_client(api_stripe_connected_accounts.app) as client:
        account = await client.post(
            "/connected_account",
            json={"stripe_account_id": "acct_123", "details_submitted": False},
        )
        assert account.status_code == 200
        account_id = account.json()["data"]["id"]

        link = await client.post(
            "/customer_account_link",
            json={"customer_id": "cust-conn", "connected_account_id": account_id},
        )
        assert link.status_code == 200

        links = (await client.get("/customer_account_link")).json()["items"]
        assert links[0]["connected_account_id"] == account_id
