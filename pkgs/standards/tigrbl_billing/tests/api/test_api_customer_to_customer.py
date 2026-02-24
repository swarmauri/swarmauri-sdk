import pytest

from tigrbl_billing.api import api_customer_to_customer


@pytest.mark.asyncio
async def test_create_transfer_records_amount(uvicorn_client):
    async with uvicorn_client(api_customer_to_customer.app) as client:
        create = await client.post(
            "/transfer",
            json={"external_id": "tr_123", "amount": 12300, "currency": "usd"},
        )
        assert create.status_code == 200

        listing = await client.get("/transfer")
        transfers = listing.json()["items"]
        assert transfers[0]["external_id"] == "tr_123"
        assert transfers[0]["amount"] == 12300
